import re
from collections import defaultdict
import csv
import math
import nltk
from nltk.corpus import stopwords

english_stopwords = stopwords.words('english')



class NaiveBayesClassifier:
    def __init__(self):
        #Initialize variables to store total vocabulary, spam_vocabulary, ham_vocabulary, total no. of spam and ham words
        self.stopwords = english_stopwords
        self.vocab = set()
        self.spam_word_count = defaultdict(int)
        self.ham_word_count = defaultdict(int)
        self.spam_total = 0
        self.ham_total = 0
        self.alpha = 1


    def remove_all_symbols(self, text):
        """Removes all symbols and characters except alphanumeric characters and whitespace."""
        return ''.join(char for char in text if char.isalnum() or char.isspace())

    #Preprocess the text
    def preprocess(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s\d¡¿]', '', text)  # Replace all non-alphanumeric characters with ''
        text = self.remove_all_symbols(text) 
        words = text.split()
        # Remove stopwords
        words = [word for word in words if word not in self.stopwords]
        return words
    
    #Train the model
    def train(self, emails, labels):
        #Run a for loop in emails and labels to extract each email and corresponding label.
        for email, label in zip(emails, labels):
            words = self.preprocess(email)
            for word in words:
                #Add all the words in the email text to our vocabulary.
                self.vocab.add(word)
                if label == 1:
                    #Increment spam word list and word count
                    self.spam_word_count[word] += 1
                    self.spam_total += 1
                else:
                    #Increment ham word list and word count
                    self.ham_word_count[word] += 1
                    self.ham_total += 1
    

    
    #Main model to predict spam or ham
    def predict(self, email):
        words = self.preprocess(email)
        spam_log_prob = self.calculate_probability(words, self.spam_word_count, self.spam_total, self.ham_total)
        ham_log_prob = self.calculate_probability(words, self.ham_word_count, self.ham_total, self.spam_total)
    
        spam_prob = math.exp(spam_log_prob)
        ham_prob = math.exp(ham_log_prob)

        prediction = True if spam_log_prob > ham_log_prob else False

        # Calculate additional metrics
        log_prob_diff = spam_log_prob - ham_log_prob
        prob_ratio = (spam_prob + 1e-10) / (ham_prob + 1e-10)

        if prob_ratio > 2.5:
            confidence = "High Confidence"
        elif prob_ratio > 0:
            confidence = "Medium Confidence"
        else:
            confidence = "Low Confidence"

        # Get top N indicative features
        top_n = 10
        indicative_features = []


        words_in_training = []


        for word in words:
            if word in self.vocab:
                words_in_training.append(word) #Add found words to the new list
        if prediction == 1:
            for word, count in sorted(self.spam_word_count.items(), key=lambda x: x[1], reverse=True):
                # Check if word is only letters
                if word.isalpha():
                    indicative_features.append((word, count))
                    if len(indicative_features) == top_n:  # Stop after 10 elements
                        break
        else:
            for word, count in sorted(self.ham_word_count.items(), key=lambda x: x[1], reverse=True):
                # Check if word is only letters
                if word.isalpha():
                    indicative_features.append((word, count))
                    if len(indicative_features) == top_n:
                        break


        return prediction, log_prob_diff, confidence, indicative_features, words_in_training
    
    #Main function to calculate probability
    def calculate_probability(self, words, word_count, total, other_total):
        prob = 0
        for word in words:
            if word in self.vocab:
                prob += math.log((word_count[word] + self.alpha) / (total + self.alpha * len(self.vocab)) + 1e-10)
            else:
                #Laplace smoothing for unseen words
                prob += math.log((self.alpha + 1) / (total + 1 + self.alpha * len(self.vocab)) + 1e-10)
        #Adjust probability for class imbalance
        prob += math.log((total + 1) / (total + other_total + self.alpha + 2))
        return prob
    
emails = []
labels = []

#Function to read the csv file
def read_csv(file_path):
    emails = []
    labels = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            labels.append(1 if row['Category'] == 'spam' else 0)
            emails.append(row['Message'])
    return emails, labels


emails, labels = read_csv('./phisingmail.csv')

classifier = NaiveBayesClassifier()
classifier.train(emails, labels)

test_email = "news and tv on your pc hi - i thought you might be interested in silicon http : / / www . silicon . com - it 's the best service i ' ve seen for it news and information . what 's really unique about it is that it has information that 's really relevant to my job and very good quality tv news and interviews . you should be able to check out the latest news by going to the inbox http : / / www . silicon . com / bin / bladerunner ? 30reqevent , + reqauth , 21046 what 's more there 's a chance of winning a sony dvd player ever week in october - all you have to do is register and use the service ."
prediction, log_prob_diff, confidence, indicative_features, words_in_training = classifier.predict(test_email)

#print("Predicted class:", "spam" if prediction == 1 else "not spam")


#print(f"Log Probability Difference: {log_prob_diff:.4f}")

#print(f"Classification Confidence: {confidence}")
#print("\nTop Indicative Features:")
#for word, count in indicative_features:
#    print(f"{word}: {count}")
#print("\nMatching Words:")
#for word in words_in_training:
#    print(f"{word}")
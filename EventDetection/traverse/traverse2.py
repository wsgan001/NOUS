import numpy
# from keras.datasets import imdb
from keras.models import Sequential
# from keras.models import Model
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
# from keras.preprocessing import sequence
from pushbullet import Pushbullet
import sklearn.metrics as sm
import sys


pl = int(sys.argv[1])

# Pushbullet Notification
pb = Pushbullet('API Key')
pb.push_note('LSTM Job Started!', ' ')

# load the dataset but only keep the top n words, zero the rest
top_words = 225
directory = 'data/wordnet/'
all_samples = numpy.genfromtxt(directory + 'all_samples_' + str(pl) + '.txt').astype('int32')

y = all_samples[:, -1]
all_samples = all_samples[:, :-1]

tot_idc = all_samples.shape[0]
tr_idc = 2 * tot_idc // 3
va_idc = 5 * tot_idc // 6

y_train = y[:tr_idc]
y_valid = y[tr_idc+1:va_idc]
y_test = y[va_idc+1:]

X_train = all_samples[:tr_idc, :]
X_valid = all_samples[tr_idc+1:va_idc, :]
X_test = all_samples[va_idc+1:, :]

# create the model
max_review_length = 2 * pl + 1
embedding_vector_length = 32
model = Sequential()
model.add(Embedding(top_words, embedding_vector_length, input_length=max_review_length))
model.add(LSTM(100))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, validation_data=(X_valid, y_valid), epochs=3, batch_size=64)

# Final evaluation of the model
scores = model.evaluate(X_test, y_test, verbose=0)
predicts = model.predict(X_test)

# Thresholding
tpredicts = [1 if x >= 0.5 else 0 for x in predicts]

print('______________________________________________________')

acc = 'Accuracy: %.2f%%' % (scores[1]*100)
print(acc)
print('__________________')
print('Confusion Matrix:')
print sm.confusion_matrix(y_test, tpredicts)
labels = ['Positive', 'Negative']
print('__________________')
print('Classification Report:')
print sm.classification_report(y_test, tpredicts, target_names=labels)

# Pushbullet Notification
pb.push_note(acc, 'Done')
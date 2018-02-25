from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Dropout, Flatten, Dense
from keras import backend as K
import collections
import os
import pandas as pd
import utils

os.getcwd()
train_dir, validation_dir, test_dir = utils.prepare_data_flow_directory(
                            train_dir_original='D:\\train\\train', 
                            test_dir_original='D:\\test\\test',
                            target_base_dir='D:\\data')

img_width, img_height = 150, 150
nb_train_samples = 2000
nb_validation_samples = 1000
nb_test_samples = 12500
epochs = 30
batch_size = 20

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)
    
model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu',input_shape=input_shape))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dropout(0.5))
model.add(Dense(512, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
print(model.summary())


model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])


train_datagen = ImageDataGenerator(rescale=1./255)

validation_datagen = ImageDataGenerator(rescale=1. / 255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary')

validation_generator = validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary')

history = model.fit_generator(
    train_generator,
    steps_per_epoch=nb_train_samples//batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=nb_validation_samples//batch_size)

model.save('cats_and_dogs_small_1.h5')

historydf = pd.DataFrame(history.history, index=history.epoch)

utils.plot_loss_accuracy(history)

test_datagen = ImageDataGenerator(rescale=1. / 255)

test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
print(test_generator.filenames)
probabilities = model.predict_generator(test_generator, nb_test_samples//batch_size)

mapper = {}
i = 0
for file in test_generator.filenames:
    id = int(file.split('\\')[1].split('.')[0])
    mapper[id] = probabilities[i][0]
    i += 1
tmp = pd.DataFrame({'id':list(mapper.keys()),'label':list(mapper.values())})
tmp.to_csv('submission.csv', columns=['id','label'],index=False)

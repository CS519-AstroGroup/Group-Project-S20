# -*- coding: utf-8 -*-
"""VELA_spec_tf.keras.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Zbj287NcX9HdhhqezH53GHFPKxrryDZx

11/08/2019  Had split labels to train individually. Combining labels and training all
            at once (except redshift). Incorporated R2 values into plots. Reviewed 
            input data (specs and labels). 
11/09/2019  Seems validation data is used for testing the model. Might introduce biases.
            Check with Sultan. 
            Added momentum to SGD optimizer. R2 generally increased.
            Added nesterov momemtum and decay rate to SGD optimizer. R2 generally 
            increased. 
            Augmented data to double input data set. R2 score marginally
            increased. Enlarging input data set.
            Added 90K shifted spectra. R2 decreased with 20 epochs. Reverting.
11/11/19    Higher decay rate (E-1 vs E-6) for optimizer drastically affects R2
            negatively. Lower decay rate (E-10) slightly affects it negatively. 
            
"""

import numpy as np
import matplotlib.pyplot as plt
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import random
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
import sklearn
from sklearn.metrics import r2_score

#from google.colab import files
#uploaded = files.upload()

#d             = np.load('data.zip') # set up to work with CIV, but can change to MgII, Lya, OVI, whatever you like :)
spec1 = np.loadtxt('./data/MgII2796data.txt')
spec2 = np.loadtxt('./data/MgII2803data.txt')
labels = np.loadtxt('./data/labels.txt')


for i in range(3):

  print (labels[:,i].shape)

  labels[:,i] -=  np.mean( labels[:,i]) 

  labels[:,i] /=  np.std( labels[:,i])



spec = np.concatenate( (np.expand_dims(spec1, axis=2), np.expand_dims(spec2, axis=2)), axis=2)
(1000000, 450, 2)

#labels: velocity, logN, doppler b
    
'''
#data augmentation to increase input data set
specs_to_add=30000
arr = np.zeros([specs_to_add,250])
arr_labels = np.zeros([specs_to_add,6])
for i in range(specs_to_add):
    shift = np.random.randint(specs_pre_aug.shape[1])
    row = np.random.randint(specs_pre_aug.shape[0])
    arr[i]=np.roll(specs_pre_aug[row], shift)
    arr_labels[i]=labels_pre_aug[row]
specs=np.concatenate((specs_pre_aug, arr), axis=0)    
labels=np.concatenate((labels_pre_aug, arr_labels), axis=0)
'''   
 
num_specs     = spec.shape[0]  
spec_pixels   = spec.shape[1]
rad           = np.random.randint(num_specs)
example_spec  = spec[rad]
example_label = labels[rad]


fig, ax = plt.subplots(1)
ax.plot(range(len(example_spec)), example_spec)
#fig, ax1 = plt.subplots(1)
#ax1.plot(range(len(labels[:,2])), labels[:,2])


"random spec", rad, "total number", num_specs, "pixels", spec_pixels , "line properties", example_label

x_train, x_test, y_train, y_test = train_test_split(spec,labels, test_size=0.1, random_state=42)

x_train.shape, x_test.shape, y_train.shape, y_test.shape
#x_train = np.expand_dims(x_train,axis=2) # making 3D for keras model
#x_test = np.expand_dims(x_test,axis=2) # making 3D for keras model

num_input      = 450
num_classes    = 3
epochs   = 100
batch_size       = 32

model = tf.keras.Sequential()

model.add(layers.Conv1D(filters=32, kernel_size=3, use_bias=False, input_shape=(num_input,2)))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
#model.add(layers.MaxPool1D(pool_size=2,strides=2))
model.add(layers.Conv1D(filters=64, kernel_size=3, use_bias=False))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Flatten())
model.add(layers.Dense(units=128, use_bias=False))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Dense(units=128, use_bias=False))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Dense(units=128, use_bias=False))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Dense(units=num_classes, use_bias=False))

model.compile(loss='mse',optimizer=tf.keras.optimizers.Adam(lr=1e-6,decay=1e-5),metrics=['accuracy'])
model.fit(x_train, y_train, batch_size=batch_size,epochs=epochs,verbose=1,validation_data=(x_test, y_test))

#model.summary() # print information about the model layer types, shapes, number of parameters

final_pred = model.predict(x_test, batch_size=batch_size, verbose=1) # use model.predict to make predictions for some subset of the data

print(final_pred.shape)


fig, ax = plt.subplots(1,num_classes, figsize=(20,4))
nn=0
ii=0      
titles = ["Velocity", "logN", "b"]
for ii in range(num_classes):
    print(ii)
    R2  = sklearn.metrics.r2_score(y_test[:,nn],final_pred[:,nn])
    ax[ii].set_title(titles[ii])
    ax[ii].set_ylabel('the predicted values')
    ax[ii].set_xlabel('the true values')
    ax[ii].annotate('R2='+('%0.3f' % R2 )+'',xy=(0.05,0.9),xycoords=
  'axes fraction',bbox=dict(boxstyle="round",fc="w"), size=14)
    ax[ii].plot(y_test[:,nn], y_test[:,nn], 'k-') # where the trend should be
    ax[ii].plot(y_test[:,nn], final_pred[:,nn], 'bo', mfc='white', alpha=0.5)
    nn+=1
fig.tight_layout()
fig.savefig('plot.png')
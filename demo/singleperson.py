import csv
import glob
from itertools import chain
from typing import Any, List

import matplotlib
import pandas as pd
import numpy as np
from IPython.core.display import display
from numpy.core._multiarray_umath import ndarray
from pandas import DataFrame

matplotlib.use("TKAgg")
from matplotlib import pyplot as plt
from util.config import load_config
from nnet import predict
from util import visualize
from dataset.pose_dataset import data_to_input
from sklearn.metrics import confusion_matrix

# import resize_images

cfg = load_config("pose_cfg.yaml")

# Load and setup CNN part detector
sess, inputs, outputs = predict.setup_pose_prediction(cfg)

# Read images from a path
# pose_image_resources_rw = "../pose_images/DownwardDog/*.jpeg" # 292 + 64 - Score 0,876
pose_image_resources ="../pose_images/all/*.jpeg"
# Uncomment this line and comment line before for development purposes (increase time execution)£
# pose_image_resources = "../pose_images/acc/*.jpeg" # 26 samples 6 testing set --> Score 0,767 (n_estimators=40, max_depth=20) 0,916
# pose_image_resources ="../pose_images/all_tree/*.jpeg"
# Images normalization --> using resize_images.py script

features = []
picture_name = []

pose_dic = ['downward', 'plank', 'warrior', 'tree']
boolean_dic = ['right', 'wrong']

# Read all images, call cnn model and make predictions about human main body parts
for images in glob.glob(pose_image_resources):
    try:
        image_name = images.title()
        image = plt.imread(images)
        picture_name.append(image_name)
        image_batch: ndarray = data_to_input(image)

        # Compute prediction with the CNN
        outputs_np = sess.run(outputs, feed_dict={inputs: image_batch})

        scmap, locref, _ = predict.extract_cnn_output(outputs_np, cfg)

        # Extract maximum scoring location from the heatmap, assume 1 person
        pose: ndarray = predict.argmax_pose_predict(scmap, locref, cfg.stride)
        # print(pose.toarr)

        # Visualise
        # visualize.show_heatmaps(cfg, image, scmap, pose)
        # visualize.waitforbuttonpress()

        features_df = list(chain.from_iterable(pose))
        y0 = '_'
        features_df.append(y0)
        y1 = '_'
        features_df.append(y1)
        features.append(features_df)

        # print(features_df)
        # this needs reshape --> features_pandas = pd.DataFrame(features_df, columns=labels)
        # dataFrame from 1d nparray --> df = pd.DataFrame(a.reshape(-1, len(a)), columns=labels)
    except Exception as e:
        print(e)

labels: List[Any] = ['x_ankle_l', 'y_ankle_l', 'error_ankle_l',
                     'x_ankle_r', 'y_ankle_r', 'error_ankle_r',
                     'x_knee_l', 'y_knee_l', 'error_knee_l',
                     'x_knee_r', 'y_knee_r', 'error_knee_r',
                     'x_hip_l', 'y_hip_l', 'error_hip_l',
                     'x_hip_r', 'y_hip_r', 'error_hip_r',
                     'x_wrist_l', 'y_wrist_l', 'error_wrist_l',
                     'x_wrist_r', 'y_wrist_r', 'error_wrist_r',
                     'x_elbow_l', 'y_elbow_l', 'error_elbow_l',
                     'x_elbow_r', 'y_elbow_r', 'error_elbow_r',
                     'x_shoulder_l', 'y_shoulder_l', 'error_shoulder_l',
                     'x_shoulder_r', 'y_shoulder_r', 'error_shoulder_r',
                     'x_chin', 'y_chin', 'error_chin',
                     'x_forehead', 'y_forehead', 'error_forehead', 'y0', 'y1']  # 44

features = np.asarray(features)
features_df: DataFrame = pd.DataFrame(features)
features_df.columns = labels

features_df['picture_name'] = picture_name
features_df.loc[features_df['picture_name'].str.contains('Right'), 'is_right'] = 1
features_df.loc[features_df['picture_name'].str.contains('Wrong'), 'is_right'] = 0
# features_df['is_right_again_2'] = features_df['picture_name'].apply(lambda x: 1 if features_df['picture_name'].str.contains('Right') else 0)
# features_df['index'] = picture_name
# features_df = features_df.set_index('index')

features_df.loc[features_df['picture_name'].str.contains('Downward'), 'pose'] = 1
features_df.loc[features_df['picture_name'].str.contains('Plank'), 'pose'] = 2
features_df.loc[features_df['picture_name'].str.contains('Tree'), 'pose'] = 3
features_df.loc[features_df['picture_name'].str.contains('Warrior'), 'pose'] = 4

# features_df.to_csv('prepared_data_499.csv')

# for string in features_df['picture_name']:
#     if 'downward' in string:
#         y1.append(1)
#         print("entra en el caso 1")
#     elif 'plank' in string:
#         y1.append(2)
#         print("entra en el caso 2")
#     elif 'tree' in string:
#         y1.append(3)
#         print("entra en el caso 3")
#     elif 'warrior' in string:
#         y1.append(4)
#         print("entra en el caso 4")
#     # To label "unknown" poses
#     # else:
#         # y1.append(5)
#         # print("entra en el caso unknown")
#
# # Create a column from the list
# features_df['y1'] = y1
# features_df = features_df.append(y1)

pd.set_option('display.max_columns', None)
display(features_df.head(10))
features_df.to_csv('prepared_data_tree.csv')

# # Load dataset
# data = pd.read_csv(file_name, sep=';')
#
# # Display records
# display(data.head(n=2))
#
# data.isnull().any()
#
# data.describe()
#
# data.info()
#
# # Some more additional data analysis
# display(np.round(data.describe()))

# display(features_df.isnull().any())
# display(pd.plotting.scatter_matrix(features_pd_df, figsize=(40, 40), diagonal='kde'))
# plt.show()
# display(features_pd_df.head(n=3))
# display(features_pd_df.describe(include="all"))
# Guardar las coordenadas y pasarselo al RF o al SVM


from sklearn.model_selection import train_test_split

# Split the data into features and target label
# features_df = features_df.drop(['picture_name', 'y0', 'y1', 'x_knee_l', 'y_knee_l', 'error_knee_l', 'x_knee_r', 'y_knee_r', 'error_knee_r'], axis=1)
features_df = features_df.drop(['picture_name', 'y0', 'y1'], axis=1)

# FEATURES PARA MODELO 1
# is_right_raw = features_df['is_right']
# features_raw = features_df.drop(['is_right'], axis=1)
# tree pose right and wrong --> Score 0.4148717948717949 , 258 samples

# FEATURES PARA MODELO 2
is_right_raw = features_df['pose']
features_raw = features_df.drop(['pose'], axis=1)


# Split the 'features' and 'income' data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features_raw,
                                                    is_right_raw,
                                                    test_size=0.2,
                                                    random_state=42)

# Show the results of the split
print("Training set has {} samples.".format(X_train.shape[0]))
print("Testing set has {} samples.".format(X_test.shape[0]))




# Initialize the randomForest model
# TODO: ver como se comporta el modelo con error y sin error
# Import any three supervised learning classification models from sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression

# Initialize the three models
reg = RandomForestRegressor(n_estimators=40, max_depth=20)
reg.fit(X_train, y_train)

y_pred = reg.predict(X_test)

from sklearn.metrics import r2_score
sco = reg.score(X_test, y_test)
R2 = r2_score(y_test, y_pred)
print("R2", R2)
print("Score", sco)

# confusion_matrix(y_test, y_pred)
plt.show()
# X_train=
# y_train=
# reg = RandomForestRegressor(min_samples_leaf=9, n_estimators=100)
# reg.fit(X_train, y_train)


def write_csv(position_data, file_name, save_error=True):
    if save_error:
        out = csv.writer(open(file_name, "a"), delimiter=',')
        out.writerow(position_data)
    else:
        pass
    # Pose, ankle, knee, hip, wrist, elbow, shoulder, chin, forehead --> 42 coord

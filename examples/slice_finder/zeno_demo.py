from slice_finder import *
from foo import *

# data_name = filename of metric dataframe
# X_colname = a list of coloumn names of features, including id coloumn
# Y_colname = a string of coloumn name of the true label
# id_colname = id coloumn name
# output_colname = (predicted) output coloumn name
# metric_fn = metric function
# slice_num = number of problematic slices to find
# degree_val = maxium number of crossing features
# size_min_val = minimum size of problematic slices
# epsilon_val = minimum effect size
# max_workers_val =


def find_slice_main(data_name, X_colname, Y_colname, id_colname, output_colname, metric_fn, slice_num, degree_val, size_min_val=0, epsilon_val=0.4, max_workers_val=4):
    full_data = pd.read_csv(
        data_name, 
        sep=r'\s*,\s*', engine='python', na_values="?")

    # full_data = full_data.dropna()

    encoders = {}
    for column in full_data.columns:
        if full_data.dtypes[column] == np.object:
            le = LabelEncoder()
            # full_data[column] = le.fit_transform(full_data[column])
            le.fit_transform(full_data[column])
            encoders[column] = le
            print(column, le.classes_, le.transform(le.classes_))

    X = full_data[X_colname]
    y = full_data[Y_colname]

    pickle.dump(encoders, open("encoders.pkl", "wb"), protocol=2)

    sf = SliceFinder((X, y), full_data, id_colname, output_colname, metric_fn, size_min_val)

    recommendations = sf.find_slice(k=slice_num, epsilon=epsilon_val, degree=degree_val, max_workers=max_workers_val)

    for s in recommendations:
        print ('\n=====================\nSlice description:')
        for k, v in list(s.filters.items()):
            values = ''
            if k in encoders:
                le = encoders[k]
                for v_ in v:
                    # values += '%s '%(le.inverse_transform(v_)[0])
                    values += '%s '%((v_)[0])
            else:
                for v_ in sorted(v, key=lambda x: x[0]):
                    if len(v_) > 1:
                        values += '%s ~ %s'%(v_[0], v_[1])
                    else:
                        values += '%s '%(v_[0])
            print ('%s:%s'%(k, values))
        print ('---------------------\neffect_size: %s'%(s.effect_size))
        print ('---------------------\nmetric: %s'%(s.metric))
        print ('size: %s'%(s.size))
    
    return recommendations


# Cifar_zeon example
data_name = "cifar_zeno.csv"
X_colname = ['id', 'blue_border_count', 'red_count', 'border_brightness', 'brightness', 'label']
Y_colname = 'label'
id_colname = 'id'
output_colname = 'output'
metric_fn = accuracy_metric
slice_num = 10
size_min_val = 20
epsilon_val = 0.4
degree_val = 2
max_workers_val = 4

find_slice_main(data_name, X_colname, Y_colname, id_colname, output_colname, metric_fn, slice_num, degree_val, size_min_val, epsilon_val, max_workers_val=4)

# Audio example
data_name = "audio.csv"
X_colname = ['0id', '0label', '0speaker', '0take', '1amplitude', '1length']
Y_colname = '0label'
id_colname = '0id'
output_colname = 'label'
metric_fn = accuracy_metric_audio
slice_num = 10
size_min_val = 20
epsilon_val = 0.4
degree_val = 2
max_workers_val = 4

find_slice_main(data_name, X_colname, Y_colname, id_colname, output_colname, metric_fn, slice_num, degree_val, size_min_val, epsilon_val, max_workers_val=4)

# zeno_data = pd.read_csv(
#     "clean_audio.csv", 
#     sep=r'\s*,\s*', engine='python', na_values="?")
# print(zeno_data.columns)
# print(zeno_data.head())

# # drop nan values
# zeno_data = zeno_data.dropna()

# # Encode categorical features
# encoders = {}
# for column in zeno_data.columns:
#     if zeno_data.dtypes[column] == np.object:
#         le = LabelEncoder()
#         zeno_data[column] = le.fit_transform(zeno_data[column])
#         encoders[column] = le
#         print(column, le.classes_, le.transform(le.classes_))

# X = zeno_data[['id', 'blue_border_count', 'red_count', 'border_brightness', 'brightness', 'label']]
# y = zeno_data['label']

# pickle.dump(encoders, open("encoders.pkl", "wb"), protocol=2)


# # accuracy_metric: should be the larger the worse
# sf = SliceFinder((X, y), zeno_data, 'id', 'output', accuracy_metric)
# # metrics_all = sf.evaluate_model((X,y))
# # reference = (np.mean(metrics_all), np.std(metrics_all), len(metrics_all))

# reference = sf.evaluate_model((X,y))

# # Find problematic slices
# # k = number of problematic slices to find
# # epsilon = minimum effect size
# # alpha = significance level (how strongly the sample evidence must contradict the null hypothesis)
# # degree = maxium number of crossing features

# # should binning be customiable? 
# recommendations = sf.find_slice(k=10, epsilon=0.4, alpha=0.05, degree=2, max_workers=4)

# for s in recommendations:
#     print ('\n=====================\nSlice description:')
#     for k, v in list(s.filters.items()):
#         values = ''
#         if k in encoders:
#             le = encoders[k]
#             for v_ in v:
#                 values += '%s '%(le.inverse_transform(v_)[0])
#         else:
#             for v_ in sorted(v, key=lambda x: x[0]):
#                 if len(v_) > 1:
#                     values += '%s ~ %s'%(v_[0], v_[1])
#                 else:
#                     values += '%s '%(v_[0])
#         print ('%s:%s'%(k, values))
#     print ('---------------------\neffect_size: %s'%(s.effect_size))
#     print ('---------------------\nmetric: %s'%(s.metric))
#     print ('size: %s'%(s.size))


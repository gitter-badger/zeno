from slice_finder import *
from foo import *

zeno_data = pd.read_csv(
    "cifar_zeno.csv", 
    sep=r'\s*,\s*', engine='python', na_values="?")

# drop nan values
zeno_data = zeno_data.dropna()

# Encode categorical features
encoders = {}
for column in zeno_data.columns:
    if zeno_data.dtypes[column] == np.object:
        le = LabelEncoder()
        zeno_data[column] = le.fit_transform(zeno_data[column])
        encoders[column] = le
        print(column, le.classes_, le.transform(le.classes_))

X = zeno_data[['id', 'blue_border_count', 'red_count', 'border_brightness', 'brightness']]
y = zeno_data['label']

pickle.dump(encoders, open("encoders.pkl", "wb"), protocol=2)


# accuracy_metric: should be the larger the worse
sf = SliceFinder((X, y), zeno_data, 'id', 'output', accuracy_metric)
# metrics_all = sf.evaluate_model((X,y))
# reference = (np.mean(metrics_all), np.std(metrics_all), len(metrics_all))

reference = sf.evaluate_model((X,y))

# Find problematic slices
# k = number of problematic slices to find
# epsilon = minimum effect size
# alpha = significance level (how strongly the sample evidence must contradict the null hypothesis)
# degree = maxium number of crossing features

# should binning be customiable? 
recommendations = sf.find_slice(k=10, epsilon=0.6, alpha=0.05, degree=2, max_workers=4)

for s in recommendations:
    print ('\n=====================\nSlice description:')
    for k, v in list(s.filters.items()):
        values = ''
        if k in encoders:
            le = encoders[k]
            for v_ in v:
                values += '%s '%(le.inverse_transform(v_)[0])
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

print('/////////////////////////////////////')

filtered, rejected = sf.filter_by_effect_size(recommendations, reference)

for s in filtered:
    print ('\n=====================\nSlice description:')
    for k, v in list(s.filters.items()):
        values = ''
        if k in encoders:
            le = encoders[k]
            for v_ in v:
                values += '%s '%(le.inverse_transform(v_)[0])
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

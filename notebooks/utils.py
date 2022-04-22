from statsmodels.stats.proportion import proportion_confint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

breaks_all = {
    'account_amount_added_12_24m': [1,25,35], 
              'age': [22.0,26.0,44.0], 'has_paid': [1.0], 
              'max_paid_inv_0_12m': [1.0,6.7,7.7], 
              'max_paid_inv_0_24m': [1.0,7.0,8.0], 
              'new_merchant_group': [2.0,3.0,4.0], 
              'num_active_inv': [1.0,2.0], 
              'num_arch_dc_0_12m':[1.0,2.0,3.0],
              'num_arch_dc_12_24m':[1.0,2.0,3.0],
              'num_arch_ok_0_12m': [1.0,2.0], 
              'num_arch_ok_12_24m': [1.0,4.0,12.0], 
              'num_arch_rem_0_12m': [1.0,2.0], 
              'num_unpaid_bills': [1.0,2.0,5.0], 
              'status_2nd_last_archived_0_24m': [1.0,2.0,3.0], 
              'status_3rd_last_archived_0_24m': [1.0,2.0,3.0], 
              'status_last_archived_0_24m': [1.0,2.0,3.0], 
              'status_max_archived_0_12_months': [1.0,2.0,3.0], 
              'status_max_archived_0_24_months': [1.0,2.0,3.0], 
              'status_max_archived_0_6_months': [1.0,2.0,3.0], 
              'sum_capital_paid_account_0_12m': [1.0,32.0,52.0], 
              'sum_capital_paid_account_12_24m': [1.0,28.0,48.0], 
              'sum_paid_inv_0_12m': [1.0, 10.5,13.5], 
              'time_hours': [8.0,10.0,18.0,21.0,22.0],
              'recovery_debt':[0.1,6.0],
              'account_status': [1.0,2.0,3.0,4.0], 
             'account_worst_status_0_3m': [1.0,2.0,3.0], 
             'account_worst_status_12_24m': [1.0,2.0,3.0,4.0], 
             'account_worst_status_3_6m': [1.0,2.0,3.0,4.0], 
             'account_worst_status_6_12m': [1.0,2.0,3.0,4.0], 
             'worst_status_active_inv': [1.0,2.0,3.0],
            'account_incoming_debt_vs_paid_0_24m':[0.01,10],
            'account_days_in_dc_12_24m': [1.0,10.0],
            'account_days_in_rem_12_24m': [1.0,10.0,20,0],
            'account_days_in_term_12_24m': [1.0,10.0,20,0]
}


final_features = ['account_worst_status_0_3m', 'age', 'max_paid_inv_0_12m',
       'max_paid_inv_0_24m', 'num_arch_dc_0_12m', 'num_arch_rem_0_12m',
       'num_unpaid_bills', 'status_last_archived_0_24m',
       'sum_capital_paid_account_0_12m', 'sum_paid_inv_0_12m',
       'new_merchant_group', 'boolean_status_last_archived_0_24m',
       'boolean_account_worst_status_0_3m']

def show_missing_value(df_tmp):
    df_tmp = (df_tmp.isnull().sum()[df_tmp.isnull().sum() > 0]/len(df_tmp))\
        .round(2).sort_values(ascending=False).reset_index()
    df_tmp.columns = ["feature","missing_percent"]
    return df_tmp

def show_defrate(df_tmp,column):
    df_tmp = df_tmp.copy()
    df_tmp['isNull'] = df_tmp[column].isnull().astype(str)
    df_tmp = df_tmp.groupby(['isNull']).default.agg(['count','sum','mean'])
    df_tmp = df_tmp.rename(columns = {"count":"num",'sum':'defaults','mean':'default_rate'})
    df_tmp['lower95'] = df_tmp.apply(lambda x:proportion_confint(count=x['defaults'], nobs=x['num'])[0],axis=1)
    df_tmp['upper95'] = df_tmp.apply(lambda x:proportion_confint(count=x['defaults'], nobs=x['num'])[1],axis=1)
    return df_tmp

def show_notnull_defrate(df_tmp,column):
    df_tmp = df_tmp.groupby([column]).default.agg(['count','sum','mean'])
    df_tmp = df_tmp.rename(columns = {"count":"num",'sum':'defaults','mean':'default_rate'})
    df_tmp['lower95'] = df_tmp.apply(lambda x:proportion_confint(count=x['defaults'], nobs=x['num'])[0],axis=1)
    df_tmp['upper95'] = df_tmp.apply(lambda x:proportion_confint(count=x['defaults'], nobs=x['num'])[1],axis=1)
    return df_tmp

def create_new_merchant_group(df_tmp):

    for merchant_category in ['Video Games & Related accessories','Cosmetics','Dating services']:
        df_tmp['merchant_group']=df_tmp.apply(lambda x: merchant_category if (x['merchant_category']==merchant_category) else x['merchant_group'], axis=1)

    merchant_dict = {'Entertainment': 1.0, 'Children Products': 2.0, 
        'Health & Beauty': 2.0, 'Intangible products': 3.0, 'Jewelry & Accessories': 3.0, 
        'Leisure, Sport & Hobby': 3.0, 'Home & Garden': 3.0, 'Automotive Products': 4.0, 
        'Clothing & Shoes': 4.0, 'Electronics': 4.0, 'Cosmetics': 5.0, 'Erotic Materials': 5.0, 
        'Video Games & Related accessories': 5.0, 'Food & Beverage': 6.0, 'Dating services': 6.0}
    
    df_tmp['new_merchant_group']=df_tmp.merchant_group.apply(lambda x: merchant_dict[x])
    
    return df_tmp

def data_clean_production(df_tmp,columns_encode=['account_worst_status_0_3m', 'status_last_archived_0_24m']):
    df_tmp = create_new_merchant_group(df_tmp)
    df_tmp = df_tmp.fillna(0.0)
    
    for column in columns_encode:
        df_tmp['boolean_'+column] = df_tmp[column].apply(lambda x: int(x!=0) )
        
    df_tmp = df_tmp.drop(["merchant_group","merchant_category"],1)
    return df_tmp


def plot_feature_importance(rf_tmp,X_tmp):
  importances = rf_tmp.feature_importances_
  #std = np.std([tree.feature_importances_ for tree in forest.n_estimators], axis=0)

  indices = np.argsort(importances)[::-1]

  # Print the feature ranking
  print("Feature ranking:")
  num_feature = X_tmp.shape[1]
  columns_ordered =[]
  importance_ordered = []
  for f in range(num_feature):
      print("%d. feature %s (%f)" % (f + 1, X_tmp.columns[indices[f]],
                                    importances[indices[f]]))
      columns_ordered.append(X_tmp.columns[indices[f]])
      importance_ordered.append(importances[indices[f]])

  # Plot the feature importances of the forest
  plt.figure(figsize=(15,5))
  plt.title("Feature importances")
  plt.bar(range(num_feature), importances[indices],
        color="r", align="center")
  #color="r", yerr=std[indices], align="center")
  plt.xticks(range(num_feature), indices)
  plt.xlim([-1, num_feature])
  plt.show()

  df_tmp = pd.DataFrame(columns=['feature','importance'])
  df_tmp['feature']=columns_ordered
  df_tmp['importance']=importance_ordered
  return df_tmp

def plot_RocCurve_models(X,y,classifier_list,name_list, show=True):
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_curve,auc

    if show == True:
        plt.figure(1,figsize=(10,7))
        plt.plot([0, 1], [0, 1], 'k--')

    roc_dict={}
    for classifier,name in zip(classifier_list,name_list):
        y_pred = classifier.predict_proba(X)[:, 1]
        fpr_rf, tpr_rf, _ = roc_curve(y, y_pred)
        roc_auc_rf = auc(fpr_rf, tpr_rf)
        if show == True:
                plt.plot(fpr_rf, tpr_rf, lw=1, label='%s (AUC = %0.3f)' % ( name, roc_auc_rf))
        roc_dict[name]=roc_auc_rf

    if show == True:
        plt.xlabel('False positive rate')
        plt.ylabel('True positive rate')
        plt.title('ROC curve')
        plt.legend(loc='best')
        plt.show()

    return roc_dict

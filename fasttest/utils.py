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

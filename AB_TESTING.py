#####################################################
# AB Testi ile BiddingYöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com için
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchasemetriğine odaklanılmalıdır.




#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleriab_testing.xlsxexcel’ininayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBiddinguygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç



#####################################################
# Proje Görevleri
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################

# 1. Hipotezleri Kur
# 2. Varsayım Kontrolü
#   - 1. Normallik Varsayımı (shapiro)
#   - 2. Varyans Homojenliği (levene)
# 3. Hipotezin Uygulanması
#   - 1. Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi
#   - 2. Varsayımlar sağlanmıyorsa mannwhitneyu testi
# 4. p-value değerine göre sonuçları yorumla
# Not:
# - Normallik sağlanmıyorsa direkt 2 numara. Varyans homojenliği sağlanmıyorsa 1 numaraya arguman girilir.
# - Normallik incelemesi öncesi aykırı değer incelemesi ve düzeltmesi yapmak faydalı olabilir.




#####################################################
# Veriyi Hazırlama ve Analiz Etme
#####################################################

#  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# !pip install statsmodels indirmek gerek
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_control = pd.read_excel("/Users/sinemdokmeci/PycharmProjects/measurement_problems/datasets/ab_testing.xlsx", sheet_name="Control Group")
df_test = pd.read_excel("/Users/sinemdokmeci/PycharmProjects/measurement_problems/datasets/ab_testing.xlsx", sheet_name="Test Group")


# Kontrol ve test grubu verilerini analiz ediniz.

df_control.describe().T
df_control.info()

df_test.describe().T
df_test.info()

# Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

df_control["Group Type"] = "Control"
df_test["Group Type"] = "Test"
df = pd.concat([df_control, df_test], ignore_index=True)


#####################################################
#  A/B Testinin Hipotezinin Tanımlanması
#####################################################

#  Hipotezi tanımlayınız.
#H0 : M1 = M2   -> Control ve Test'e ait Purchase değişkeni için ist. olarak anlamlı bir fark yoktur.
# H1: M1 != M2  -> Control ve Test'e ait Purchase değişkeni için ist. olarak anlamlı bir fark vardır.


# Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz
df[df["Group Type"] == "Control"]["Purchase"].mean()
df[df["Group Type"] == "Test"]["Purchase"].mean()

#####################################################
# Hipotez Testinin Gerçekleştirilmesi
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################


# Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz
#Aşşağıda ki iki şekilde de yapılabilir
shapiro(df[df["Group Type"] == "Control"]["Purchase"])[1]

test_stat, pvalue = shapiro(df[df["Group Type"] == "Test"]["Purchase"].dropna())
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
#Her iki değer için shapiro testine göre p-value değeri 0.05'ten bbüyük olduğu için H0 reddedilemez.
#Her iki değer de normallik varsayımını saülamaktadır.

#Varyans Homojenliği
levene(df[df["Group Type"] == "Control"]["Purchase"], df[df["Group Type"] == "Test"]["Purchase"])[1]

test_stat, pvalue = levene(df[df["Group Type"] == "Control"]["Purchase"],
                           df[df["Group Type"] == "Test"]["Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# İki değer arasında levene testine göre p-value değeri 0,05'ten küçük olmadığından H0 reddedilemez.
# İki değer arası Homojendir.

# Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz
#ttest_ind(df[df["Group Type"] == "Control"]["Purchase"],df[df["Group Type"] == "Test"]["Purchase"])[1] ---- Bu şekilde de yapılabilir.
test_stat, pvalue = ttest_ind(df[df["Group Type"] == "Control"]["Purchase"],
                              df[df["Group Type"] == "Test"]["Purchase"],
                              equal_var=True)

print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# İki değer arasında ttest_ind testine göre p-value değeri 0,05'ten küçük olmadığından H0 reddedilemez.
# İki değer arasında ist. olarak anlamlı bir fark yoktur.H0 hipotezi kabul edilir.

# Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

# İki değer arasında ttest_ind testine göre p-value değeri 0,05'ten küçük olmadığından H0 reddedilemez.
# İki değer arasında ist. olarak anlamlı bir fark yoktur.H0 hipotezi kabul edilir.

## Bonus : Rekram tıklanma reklam görüntülenme sayısı
control_click = df[df["Group Type"] == "Control"]["Click"].sum()
test_click = df[df["Group Type"] == "Test"]["Click"].sum()

control_impression = df[df["Group Type"] == "Control"]["Impression"].sum()
test_impression = df[df["Group Type"] == "Test"]["Impression"].sum()

test_stat, pvalue = proportions_ztest(count=[control_click, test_click], nobs=[control_impression, test_impression])


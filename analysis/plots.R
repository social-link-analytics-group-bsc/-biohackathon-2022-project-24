library(data.table)
library(ggplot2)
library(tidyverse)

df_path = "/media/victoria/VICTORIA_EXTERNAL_DISK/bh22/candidate_sentences_full_extended.csv"
df = fread(df_path, header=T, na.strings=c(""))
df$n = 1
df$sex_gender = ifelse(is.na(df$tokenized_METHODS), 'no','yes')
library(dplyr)
df_sum = df %>% group_by(sex_gender) %>% summarise(total=sum(n))
ggplot(df_sum, aes(x = sex_gender,y=total, fill = sex_gender))+
  geom_bar(stat = "identity")+
  ylab("# articles")+
  theme_minimal()+
  scale_fill_manual(values=c("blue", "yellow"))+
  theme(axis.text =element_text(size=20),axis.title = element_text(size=20))

df_sum2 = df %>% group_by(sex_gender,year) %>% summarise(total=sum(n))
df_sum2$year = as.numeric(df_sum2$year ) 
ggplot(subset(df_sum2, year>1900 & year < 2023), aes(x = year,y=total, color = sex_gender))+
  geom_line(size = 1)+
  geom_point(size = 2)+
  ylab("# articles")+
  theme_minimal()+
  scale_color_manual(values=c("blue", "yellow"))+
  theme(axis.text =element_text(size=20),axis.title = element_text(size=20))

library(dplyr)
df_sum1 = df %>% group_by(sex_gender,`journal-id`) %>% summarise(total=sum(n))
head(df_sum1)


library(ggplot2)
df_sum11 = subset(df_sum1, sex_gender == "no") %>% group_by(sex_gender) %>% arrange(sex_gender,desc(total))
head(df_sum11)
df_sum1 = subset(df_sum1, `journal-id` %in% df_sum11$`journal-id`[1:50])
df_sum1$`journal-id` = factor(df_sum1$`journal-id`, levels = df_sum11$`journal-id`)
head(levels(df_sum1$`journal-id` ))

ggplot(df_sum1, aes(y=`journal-id`,x=total, fill =sex_gender))+
  geom_bar(stat="identity", color = "black")+
  theme_minimal(  )+
  scale_fill_manual(values=c("blue", "yellow"))+
theme(axis.text.x = element_text(hjust=1,vjust=1))


df_sum3 = df %>% group_by(sex_gender,`journal-id`,year) %>% summarise(total=sum(n))
df_sum3$year = as.numeric(df_sum3$year ) 
ggplot(subset(df_sum3, year>1950 & year < 2023 & `journal-id` %in% levels(df_sum1$`journal-id`)[1:10] ),
       aes(x = year,y=total, color = sex_gender))+
  geom_line(size = 1)+
  geom_point(size = 1)+
  ylab("# articles")+
  theme_minimal()+
  scale_color_manual(values=c("blue", "yellow"))+
  theme(axis.text =element_text(size=10),axis.title = element_text(size=10),
        strip.text.y.right = element_text(angle = 0))+
  facet_grid(`journal-id`~.)

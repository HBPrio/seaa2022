#!/usr/bin/env Rscript

library(readr)
library(ggplot2)
library(nortest, pos=17) # ad.test
library(pgirmess) # kruskalmc
library(agricolae) # kruskal with tukey groups
library(RColorBrewer)

#==================================================
# Preparation
#==================================================
setwd("c:/Users/siqueira/Documents/...")

approaches <- c(
  "HB-all",
  "HB-fam"
)
v_factor_levels <- unique(approaches)

#LOAD RESULTS FILE
results_loc <- "time.csv"
raw_results <- read_delim(results_loc, ",", escape_double = FALSE, trim_ws = TRUE)

raw_results <- subset(raw_results, Approach %in% approaches)

pdf_w <- 9
pdf_h <- 6
my.cols = brewer.pal(n = 8, name = "Dark2")

#reordering and renaming
raw_results$Approach <- factor(raw_results$Approach, 
                               levels=c("HB-all","HB-fam"),
                               labels=c("Fam-ind","Fam-dep"),)

#==================================================
# Boxplots (TTFF)
#==================================================
#png("PrioTime_BoxPlot.png", width=600, height=600)
pdf("PrioTime_BoxPlot_temp.pdf", width=pdf_w, height=4)

ggplot(data=subset(raw_results), aes(Approach, Prio_Time, fill=Approach))+ 
  geom_boxplot(width=0.4, outlier.size = 3, size=1) +
  coord_flip()+
  scale_fill_manual(values = my.cols)+
  labs(y="Prioritization Time (sec)")+
  theme_light()+ 
  theme(axis.text = element_text(size = 20),
                           axis.title.y = element_text(size = 24, margin = margin(r=10)),
                           axis.title.x = element_text(size = 24, margin = margin(t=10)),
                           legend.position="none")

dev.off()

#==================================================
# Normality Test (APFD)
#==================================================
#NORMALITY TEST (AD)
#The null hypothesis for the A-D test is that the data does follow a normal distribution. 
#If p-value < significance level, the data does not follow a normal distribution.
with(raw_results, ad.test(Prio_Time))

#==================================================
# APFD
#==================================================
#Kruskal-Wallis rank sum test
with(raw_results, tapply(Prio_Time, Approach, median, na.rm=TRUE))
kruskal.test(Prio_Time ~ Approach, data=raw_results)

#Kruskal-Wallis rank sum test (MULTIPLE COMPARISON)
kruskalmc(raw_results$Prio_Time, raw_results$Approach)

# Pairwise comparisons using Wilcoxon’s test
#wilcox_test(raw_results, APFD ~ Approach, p.adjust.method = "bonferroni")

out <- kruskal(raw_results$Prio_Time, raw_results$Approach)
out
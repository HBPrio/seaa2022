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
  "OTD",
  "RO",
  "BO",
  "NewOld",
  "OHB_v01",
  "OHB_v02"
)
v_factor_levels <- unique(approaches)

#LOAD RESULTS FILE
results_loc <- "apfd.csv"
raw_results <- read_delim(results_loc, ";", escape_double = FALSE, trim_ws = TRUE)

raw_results <- subset(raw_results, Approach %in% approaches)

pdf_w <- 9
pdf_h <- 6
my.cols = brewer.pal(n = 8, name = "Dark2")

#reordering and renaming
raw_results$Approach <- factor(raw_results$Approach, 
                               levels=c("BO","OHB_v02","OHB_v01","RO","NewOld","OTD"),
                               labels=c("Optimal","Fam-dep","Fam-ind","Random","NewOld","RealOrd"))


#==================================================
# Boxplots (TTFF)
#==================================================
#png("APFD_BoxPlot.png", width=800, height=600)
pdf("APFD_BoxPlot.pdf", width=pdf_w, height=pdf_h)

ggplot(data=subset(raw_results, !is.na(APFD)), aes(Approach, APFD, fill=Approach))+ 
  geom_boxplot(outlier.size = 3, size=1)+
  scale_fill_manual(values = my.cols)+
  theme_light()+ 
  theme(axis.text = element_text(size = 20),
                           axis.title.y = element_text(size = 24, margin = margin(r=10)),
                           legend.position="none",
                           axis.title.x = element_blank())

dev.off()

#==================================================
# Normality Test (APFD)
#==================================================
#NORMALITY TEST (AD)
#The null hypothesis for the A-D test is that the data does follow a normal distribution. 
#If p-value < significance level, the data does not follow a normal distribution.
with(raw_results, ad.test(APFD))

#==================================================
# APFD
#==================================================
#Kruskal-Wallis rank sum test
with(raw_results, tapply(APFD, Approach, median, na.rm=TRUE))
kruskal.test(APFD ~ Approach, data=raw_results)

#Kruskal-Wallis rank sum test (MULTIPLE COMPARISON)
kruskalmc(raw_results$APFD, raw_results$Approach)

# Pairwise comparisons using Wilcoxon’s test
#wilcox_test(raw_results, APFD ~ Approach, p.adjust.method = "bonferroni")

out <- kruskal(raw_results$APFD, raw_results$Approach)
out
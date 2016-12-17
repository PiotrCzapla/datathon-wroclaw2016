library(tidyverse)
library(plotly)

path <- 'C:\\Users\\W³aœciciel\\Documents\\Wroc³awskie Dane\\WBO\\WBO_lista_glosow_2016.csv'
data <- read.csv(path, header = T, sep = ';')

data %>%
  mutate(tmp = Ogolno_2) %>%
  filter(tmp != 0) %>%
  inner_join(data %>%
               mutate(tmp = Ogolno_1) %>%
               filter(tmp != 0), by='tmp')

data %>%
  group_by(Zrodlo, Plec) %>%
  summarise(Wiek_sr=mean(Wiek),
            Wiek_md=median(Wiek))

data_o <- data %>%
  select(c(Ogolno_1, Ogolno_2)) %>%
  rename(pierwszy = Ogolno_1, drugi = Ogolno_2) %>%
  bind_rows(data %>%
              select(c(Ogolno_2, Ogolno_1)) %>%
              rename(pierwszy = Ogolno_2, drugi = Ogolno_1)) %>%
  filter(!(pierwszy == 0 & drugi == 0))

results <- data_o %>%
  group_by(pierwszy) %>%
  summarise(total = n()) %>%
  mutate(pct = total/sum(total))

results_second <- data_o %>%
  group_by(pierwszy, drugi) %>%
  summarise(cnt = n()) %>%
  inner_join(results, by=c('drugi' = 'pierwszy')) %>%
  group_by(pierwszy) %>%
  mutate(pct_cnd = cnt/sum(cnt),
         rel = pct_cnd/pct) %>%
  rename(cnt_both = cnt,
         cnt_drugi = total,
         pct_both = pct_cnd,
         pct_drugi = pct) %>%
  inner_join(results %>%
               rename(cnt_pierwszy = total,
                      pct_pierwszy = pct))

View(results_second %>% 
       filter(cnt_pierwszy >= 100 & cnt_drugi >= 100) %>% 
       arrange(desc(cnt_pierwszy), desc(rel)))

ggplot(results_second %>%
         filter(rel < 0.3 | rel > 3), aes(cnt_pierwszy, cnt_drugi, color = log(rel))) +
  geom_point(size = 2) + 
  scale_color_distiller(palette = 'RdBu') + 
  theme_bw()

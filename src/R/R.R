library(tidyverse)
library(plotly)

data_path <- '../../data/'
votes_2016 <- paste0(data_path, '2016-12-03-WBO_lista_glosow_2016.csv')
proj_2016 <- paste0(data_path, 'projects_2016.csv')
data <- read.csv(votes_2016, header = T, sep = ';')
proj_data <- read.csv(proj_2016, header = F, sep = ',', stringsAsFactors = F) %>%
  select(V1,V2,V3,V5,V6,V7) %>%
  rename(id = V1,
         status = V2,
         glosy = V3,
         budzet = V5,
         obszar = V6,
         kategoria = V7) %>%
  mutate(kategoria = ifelse(kategoria == 'do 750 000 zł', 
                            '750k',
                            ifelse(kategoria == 'do 250 000 zł', '250k', '1kk')),
         obszar = ifelse(obszar == 'zieleń/rekreacja', 'ziele�/rekreacja', obszar))


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

results_projects <- results_second %>%
  left_join(proj_data %>% select(id, status, obszar), by=c('pierwszy'='id')) %>%
  rename(status_1 = status,
         obszar_1 = obszar) %>%
  left_join(proj_data %>% select(id, status, obszar), by=c('drugi'='id')) %>%
  rename(status_2 = status,
         obszar_2 = obszar) %>%
  mutate(rel_bin = cut(rel/median(rel), breaks = c(0, 0.7, 1.3, Inf), 
                       labels = c('Negative', 'Neutral', 'Positive')))
results_projects[is.na(results_projects)] <- 0

results_projects %>%
  group_by(status_1, status_2) %>%
  summarise(negative = mean(rel_bin == 'Negative'),
            neutral = mean(rel_bin == 'Neutral'),
            positive = mean(rel_bin == 'Positive')) %>%
  filter(status_1 != 0)

results_projects %>%
  group_by(status_1, status_2) %>%
  summarise(mean(rel),
            median(rel)) %>%
  filter(status_1 != 0)

ggplot(results_projects %>%
         filter(obszar_1=='drogowe'), 
       aes(rel, color=paste(obszar_1, obszar_2))) + 
  geom_density() + 
  scale_x_log10() + 
  theme_bw()
ggplotly()





View(results_second %>% 
       filter(cnt_pierwszy >= 100 & cnt_drugi >= 100) %>% 
       arrange(desc(cnt_pierwszy), desc(rel)))

ggplot(results_second %>%
         filter(rel < 0.3 | rel > 3), aes(cnt_pierwszy, cnt_drugi, color = log(rel))) +
  geom_point(size = 2) + 
  scale_color_distiller(palette = 'RdBu') + 
  theme_bw()

## Module 16: Experimental design and A/B testing

Contents

* [Checkpoint 2](#Checkpoint-2)
* [Checkpoint 3](#Checkpoint-3)
* [Checkpoint 5](#Checkpoint-5)

____

#### Checkpoint 2

For each of the following questions, outline how you could use an A/B test to find an answer. Be sure to identify all five key components of an A/B test we outlined above.

1. Does a new supplement help people sleep better?
2. Will new uniforms help a gym's business?
3. Will a new homepage improve my online exotic pet rental business?
4. If I put 'please read' in the email subject will more people read my emails?

*Answers*

Framework: Break down prompt into five components: (a) identify treatment and control groups, (b) formalise sample and split sample between groups, (c) build hypothesis, (d) distinguish between key outcome variable and other variables, (e) make recommendation based on statistically significant inferences

|                                                        | Q1                                                           | Q2                                                           | Q3                                                           | Q4                                                           |
| ------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Treatment and control version                          | **Treatment**: people taking the supplement <br />**control**: people taking an indistinguishable placebo pill | **Control:** Employees wear existing uniform for a 2 week period during a non-peak time of the year, <br />**Treatment**: Employees wear different uniform for a  2 week period during a non-peak time of the year, a month after the control period | **Control**: Existing version of homepage,  <br />**Treatment:** modified version of homepage | **Control:** Email without 'please read', <br />**Treatment:** Email with same content sent at the same time to similar receivers without 'please read', |
| Sample                                                 | Groups are randomly sampled from a pool of people with similar preexisting sleep conditions | Two two-week periods are chosen a month apart such that they are non-peak (eg. January after New Year's Eve, before summer, etc.) | 10% of the incoming traffic is randomly routed into the two versions. Care must be taken to randomise segmentation, but over segmentation must be avoided. | Care must be taken to ensure that receivers are homogenous in business value (seniority, rank, size of business, etc). This sample can then be randomised. |
| Hypothesis                                             | Subjects taking the supplement sleep better                  | Hard to say                                                  | Hard to say                                                  | The treatment is likely to perform better                    |
| **Key outcome variable** + other variables of interest | **Hours slept** + energy level through the day, level of freshness in the morning, average number of interruptions during sleep | **Acquisition of new members** + existing member retention, existing members upgrading their plans, satisfaction surveys, etc | **Overall conversion rate** + CTR on initial homepage, member/mailing list signups, add to bags, time spend on site | **Mail open rate, reply rate**                               |
| Recommendation                                         | Will depend on actual experiment results                     | Will depend on actual experiment results                     | Will depend on actual experiment results                     | Will depend on actual experiment results                     |

____

#### Checkpoint 3

Call out the potential biases in the proposed experiment. Do your best to try to discover not only the bias, but the initial design. There is plenty of room for interpretation here, so make sure to state what assumptions you're making.

1. You're testing advertising emails for a bathing suit company and you test one version of the email in February and the other in May.
2. You open a clinic to treat anxiety and find that the people who visit show a higher rate of anxiety than the general population.
3. You launch a new ad billboard based campaign and see an increase in website visits in the first week.
4. You launch a loyalty program but see no change in visits in the first week.

*Answers*

1. **Selection bias:** People are more likely to open relations to bathing suits at the onset of summer (May) vs. the middle of winter (Feb). 
2. **Biased sample:** There's a degree of self-selection here. People with anxiety or anxiety-like symptoms are more likely to visit the clinic in the first place (as compared to the general public), and as such, an analysis will reveal a higher rate of anxiety. The two samples aren't randomised at all. 
3. This use case might represent a bias in selection of the key outcome variable. It is fairly intuitive that a new billboard campaign will result in increase in website visits, but the more important business variable might rather be the *order conversion rate* or an intermediary step like the *add to bag rate*. An increase in website visits doesn't confirm that a hypothesis connecting marketing spend and final revenue, but rather just marketing spend and initial acquisition numbers.  
4. A loyalty program is likely to have returns over a longer timeframe, and as such, is quite likely to not show substantial changes in the first week. 

____

#### Checkpoint 5 

1. Even though the samples are randomised, there's an **inherent contextual bias** in the manner in which the message is delivered. Darth Vader is not known for being an especially eloquent speaker (not to mention the constant deep breathing!), and as such, is likely to negatively bias the droids that listen to him. Palpatine, on the other hand, is more likely to be received as an enthusiastic recruiter (despite the content of his message), and is likely to positive bias the droids that listen to him. The experiment should be repeated with the same speaker to eliminate contextual bias. 

2. There's an **apparent selection bias**: the two assignments are not randomised, and hence can't be compared at this level. Friendly planets, by virtue of being friendly, are more likely to maintain favourable attitudes than planets that are less friends. Even if the experiment is repeated such that each envoy visits two friendly and two unfriendly planets, care must be taken to take the levels of friendliness and the planet population in account to prevent a **lurking variable bias (Simpson's paradox).**  

3. Averaging the groups across continents hides a lurking variables bias (Simpson's paradox). A more appropriate conclusion would include the comparison of IT vs HR for individual countries, keeping in account the respective number of employees.

4. This is likely a case of reporting bias. Consumers with pre-existing fitness or high ambition for fitness are more likely to be proud of their fitness stats, and as such, are more likely to 'opt-in'. On the other hand, presently unfit consumers or those with lower levels of disciplines, are more likely to be embarrassed of their fitness goals, and are less likely to want to share their goals. As such, the data will bias towards a fitter section of the population. 

   There are numerous ways to fix this experiment, but the best way is perhaps to make sure that (a) the data collection process is anonymous and aggregated at a regional level, (b) consumers are aware of this. This minimises an individual customer's concern that their lack of fitness might be negatively perceived, leading to more opt-ins from this population. Another way to increase opt-ins might be to incentives opting-in with in-app rewards/perks. 

5. The distribution of question papers that have been cumulatively stacked is likely to result in multiple cases of students sitting adjacent to each other receiving the same version of the question paper. This makes cheating easier as the students are able to compare answers with their neighbours. A better way to prevent cheating would simply be to alternate the stacking of papers, such that no student receives the same version as their neighbour. 

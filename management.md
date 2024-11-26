# Meeting one (2024-11-12):

### Atendees
- Janos
- Omid
- Henrik
- Victoria
- Yingchao

### Collaboration
We will use Git and GitLab for collaboration. We will hold meetings regularly to divide tasks between our team members and to discuss our progress. Upon dividing the tasks between members, we will use the features of GitLab (feature branches, issues, merge requests, etc.) to track our progress and aid us in collaborating. When the given feature or task has been finished by a team member, we’ll have a process of reviewing the code by other team members, for this we’ll use merge requests. These merge requests should be reviewed and approved by a team member other than the one who created it. A merge request needs to be approved before it is merged. Moreover the team will use the following format on their commits: 

```Bash
git commit -m “#<issue_number> <imperative sentence on what the commit does>”
```

### Knowledge sharing
READMEs will be used to document and describe the intended usage of code structures. This will be useful as the information will persist and will be available to whoever needs it in the future.
Comments: Ensure to add adequate code documentation, especially for those functions that are difficult to understand. Documentation should be concise and easy to read and understand by the rest of the team.
On-demand meetings: Knowledge sharing can mostly be achieved through our regular in-person meetings. For special implementations of some new ideas, on-demand meetings can be scheduled to discuss these ideas. This is a great way to keep the entire team up to date on new ideas and the progress made by each team member.

### Communication
Our communication channel of choice is Discord, where we will share advice and progress updates. We will complement this with regular in-person meetings, to ensure that no vital information is left out. Scheduled meetings will occur twice a week on Tuesdays and Fridays. Discord will be used as a means of scheduling extra meetings as needed. 

### Conflicts
In the event of conflicts, we will attempt to resolve them through communication and discussion. We will try to understand the conflict from both sides and come up with a solution. If a resolution cannot be achieved, we will vote to make decisions, based on the principle of majority rule and minority compliance. If conflicts arise between team members and cannot be resolved internally through communication, we will seek assistance from the teacher or TA.

### Tasks
All team members will be looking for more datasets and try to train dummy models to get more insight on the existing ideas until the next meeting at **2024-11-15**.

# Meeting two (2024-11-15):

### Atendees
- Janos
- Omid
- Henrik
- Victoria
- Yingchao

### Meeting Agenda
- In this meeting we decided to go with the Fraud Detection idea.
- We decided to use Django for the backend and Vue.js for the frontend.
- We decided to use Postgres for the database and having it running on one of the team member's VPS (This is to be changed later on). Later one we will use the Cloud VM for the database.
- We discussed how we will use Git and GitLab to version the code and model. We discussed how we may use  tags for versioning the code that results in different stable models.
- We discussed using Docker to containarise our code.

### Tasks

- **Victoria and Omid**: They will be working on writing the Assignment 1 report.
- **Yingchao**: He will be working on connecting to the Hosted Postgres database.
- **Janos**: He will be setting up the VPS for the database and create project infrastructure for the front-end
- **Henrik**: He will be working on developing a model to test the idea.

**Note**: Everyone will also learn and study technologies including Django, and Kubernetes
**Note**: These tasks are to be done by **2024-11-22**

# Meeting Three (2024-11-19):

### Atendees
- Janos
- Omid
- Henrik
- Victoria
- Yingchao

### Meeting Agenda

- In this meeting we discussed strategies for data versioning. We came up with the idea of using ids for versioning the dataset that we have. This allows us to choose the same dataset for model training. We also decided to have a column saying which model versiion prdeicted a particular row as fraud or not fraud. In that case, we can use the same dataset when we do dynamic training.
- We also discussed data validation and decided to use tensorflow for data validation.
- We also decided to unpack the feature velocity_last_hour which has a `JSON` format to their own features.
- We decided to use tags for versioning the code that results in different stable models.
- We discussed what tasks needed to be doen for this sprint which ends on `2024-11-29`.

### Tasks

- **Henrik**: He will be working on deployment of our app on the cloud. Here is the issue [link](https://git.chalmers.se/courses/dit826/2024/group1/-/issues/5)
- **Omid**: He will be working on versioing code that creates the model. Here is the issue [link](https://git.chalmers.se/courses/dit826/2024/group1/-/issues/7). He will also work on setting up the webiste homepage, register page, login page, and admin page. Here is the issue [link](https://git.chalmers.se/courses/dit826/2024/group1/-/issues/7).
- **Janos**: He will be working on data versioning and unpacking `JSON`format data. Here is the issue [link] (https://git.chalmers.se/courses/dit826/2024/group1/-/issues/10)
- **Victoria**: She will be working on data validation in the ML pipeline. Here is the issue [link](https://git.chalmers.se/courses/dit826/2024/group1/-/issues/9)
- **Yingchao**: He will be working on feature engineering, to see which features are the most useful and related. Here is the issue [link](https://git.chalmers.se/courses/dit826/2024/group1/-/issues/8)

# Meeting Four (2024-11-22):

### Atendees    
- Janos
- Omid
- Henrik
- Victoria  
- Yingchao

### Meeting Agenda
- We discussed what free clooud services we can use. We want to use Oracle cloud, but we are a bit confused about the `Always Free tier` ones. Herik will do some more research and choose the cloud provider he deems the best for our purpose.
- We discussed model versioning and how to train the model for each code change that affects the model.

**Notes**: Theteam is to complete the tasks that we came up with on the previous meeting by **2024-11-29**
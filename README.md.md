# JHebergeUneFamille

## What is JHebergeUneFamille ?
JHebergeUneFamille is an application that connects homeless people with individuals willing to host them temporarily and for free. For now, it is only in French.
## Requirements
Ubuntu 20+, python v3.9+, postgresql v12+

## Installation
1. Create a database on the server
2. clone the project
3. Users can upload photos. For security reasons, they are stored in an AWS S3 bucket that you need to create.
4. Emails are sent via the smtp service of Google. You will have to configure it.
5. Add the following environment variables in 'settings/production.py' :

    APP_PASSWORD: The password provided by gmail
    EMAIL_HOST: smtp.gmail.com
    EMAIL_HOST_USER: email address
    EMAIL_PORT: 587
    EMAIL_USE_TLS: True
    AWS_ACCESS_KEY_ID: Provided by AWS
    AWS_SECRET_ACCESS_KEY: Provided by AWS
    AWS_STORAGE_BUCKET_NAME: The name of the bucket
    AWS_DOMAIN_NAME: the path to access the bucket from https to .amazonaws.com/  (Eg: https://mybucket.s3.eu-west-3.amazonaws.com/)
    AWS_QUERYSTRING_AUTH: False
    
6. If you want to do CI/CD, you have to add in the 'secrets' of github the environment variables that are in the file production.py. You must also add the following variables:

    IP_ADDRESS: The IP addres of the app (Because of Continuous Deployment)
    PROJECT_FOLDER: The name of the folder that contains the app
    REPOSITORY_ADDRESS: The address of your fork
    SSH_KEY_PRIVATE: The private SSH key of your local machine
    USERNAME: The name of the user to access your remote server
    USER_PASSWORD: The password of the user on the remote server
For CI/CD, you need to have **supervisor** and **nginx** installed on the server

## Usage
**Homeless people** register and enter in the search engine the number of people to be hosted for free by volunteers (Eg: A mother and her child).
The system first indicates the cities where there is housing that meets the criteria.
By selecting a city, the person can have summary information about each accommodation in that city.
Then, by clicking on an accommodation, he can have more details.
The person can then send a message to the owner.
They can also add the owner to their contact list so they can send more messages later.

**Owners** who wish to help homeless people temporarily can register to enter the information about the accommodation they are providing. It is possible for them to offer more than one.
The email address of the owners is never communicated on the site in order to avoid the collection of data by scripts.
It is possible to indicate that an accommodation is unavailable. In this case, it will not appear in the search results.
Of course, an owner can remove his accommodation from the system at any time.

**The administrators** of the application can be contacted by any user via the "contact" link in the footer.
Messages appear in the administration panel at domain_name/admin




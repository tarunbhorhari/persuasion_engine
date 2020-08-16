This is the repository for maintaining In-Goibibo, the backend hotel inventory management system for Goibibo.
####
1. To start with development on this project, you may need to get access to Goibibo server environment. Obtain the requisite access from the networkops team for machines (IP+port) by mailing the yellow forms, and VPN accesses etc to work remotely.

2. Add the following entries in your /etc/hosts file:

	`127.0.0.1           dev.ingoibibo.com`

3. Get accesses for
	1. Goibibo account on Gmail
	2. PP cassandra
	3. JIRA (goibibo.atlassian.net)

4. To setup the project locally on your system, follow steps mentioned in setup_process.md

Ideally, given that we have a defined `Dockerfile`, a dev should just need to do build the docker image with:
```
docker build --build-arg env=dev -t ingoibibo:latest .
```

and then make the docker container up by using docker-compose:
```
export MY_HOST=`ipconfig getifaddr en0` && docker-compose -f docker-compose-dev.yml up -d
```

***Note**: The idea of `ipconfig getifaddr en0` is to get the current netowrk IP of your host machine - aka - laptop :) On Centos and Ubuntu machines you might have to use ifconfig to get the current public IP. `ipconfig` works for mac*
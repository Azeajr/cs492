FROM alpine:latest
RUN apk add --update --no-cache openssh python3 nano
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
RUN adduser -h /home/pi -s /bin/sh -D pi
RUN echo -n 'pi:sunshine' | chpasswd
ENTRYPOINT ["/entrypoint.sh"]
EXPOSE 22
COPY entrypoint.sh /
WORKDIR /home/pi
COPY /worm/passwords.txt passwords.txt
COPY /worm/usernames.txt usernames.txt
COPY /worm/requirements.txt requirements.txt
COPY /worm/ssh_worm.py ssh_worm.py
RUN python -m ensurepip --upgrade
RUN python -m pip install -r requirements.txt
# CMD ["nohup", "python", "ssh_worm.py", "&"]
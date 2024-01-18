# #Using https://www.youtube.com/watch?v=J7Fm7MdZn_E as a guide
# FROM python:3.9
# WORKDIR /workdir
# COPY /Kumiko /Kumiko
# RUN python -m venv venv
# #https://askubuntu.com/questions/504546/error-message-source-not-found-when-running-a-script
# RUN . venv/bin/activate
# RUN python -m pip install discord requests
# # CMD python -m Kumiko.main
# ENTRYPOINT [ "flyio.sh" ]


FROM python:3.9
COPY /Kumiko /Kumiko
COPY Token.py .
RUN python -m pip install discord requests
CMD ["python", "-m", "Kumiko.main"]

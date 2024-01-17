#Using https://www.youtube.com/watch?v=J7Fm7MdZn_E as a guide
FROM python:3.9
WORKDIR .
COPY /Kumiko Token.py
RUN python -m venv venv
RUN source venv/bin/activate
RUN python -m pip install discord requests
CMD python -m Kumiko.main

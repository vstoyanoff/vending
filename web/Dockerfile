FROM node:16-buster
# The SHELL statement below makes RUN commands a bit more robust and easier to debug.
# More details: https://bit.ly/2InCT2P (link to bash documentation).
SHELL ["/bin/bash", "-o", "pipefail", "-o", "errexit", "-o", "nounset", "-o", "xtrace", "-c"]

WORKDIR /home/vending/code

COPY package.json yarn.lock /home/vending/code/

RUN yarn install

COPY . /home/vending/code


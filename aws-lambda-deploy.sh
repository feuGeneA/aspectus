#!/usr/bin/env sh

# prerequisites:
#     64-bit Linux
#     python pip
#     Info-ZIP zip
#     aws cli with support for lambda
#     `aws configure`

check_prerequisites() {
    if ! uname -a | grep Linux | grep -q x86_64 ; then
        echo 'Lambda deployments must be built in an x86_64 Linux environment'
        return 1
    fi
}

build() {
    rm -rf build

    pip install geopy ephem  pytz icalendar -t ./build/socalgen

    cp *.py build/socalgen

    cd build/socalgen
    zip -r ../socalgen.zip *
    cd ../..
}

deploy() {
    aws lambda update-function-code \
        --function-name socalgen \
        --zip-file fileb://socalgen.zip
}

test_deployment() {

    rm -f socalgen\?place\=avon%20nc\&lookaheaddays\=1 \
          socalgen\?place\=avon%20nc\&lookaheaddays\=1.masked

    wget https://k9mudvqin2.execute-api.us-east-1.amazonaws.com/prod/socalgen?place=avon%20nc\&lookaheaddays=1

    if [ ! -e socalgen\?place\=avon%20nc\&lookaheaddays\=1 ]; then
        echo failed to query service
        return 1
    fi

    sed -e 's/DATE-TIME:.*/DATE-TIME:.../' socalgen\?place\=avon%20nc\&lookaheaddays\=1 > socalgen\?place\=avon%20nc\&lookaheaddays\=1.masked

    diff socalgen\?place\=avon%20nc\&lookaheaddays\=1.masked ../socalgen\?place\=avon%20nc\&lookaheaddays\=1.masked.expected

    if [ $? -eq 0 ]; then
        echo deployment successful
    else
        echo test failed
        return 1
    fi
}

check_prerequisites || exit 1
build || exit 1
cd build
deploy || exit 1
test_deployment || exit 1

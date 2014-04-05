#!/bin/sh

kill `ps aux | grep skype2irc | grep -v grep | awk '{print $2;}'`

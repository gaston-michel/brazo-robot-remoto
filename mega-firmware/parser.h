#ifndef PARSER_H
#define PARSER_H

#include <Arduino.h>

// Initialize parser
void initParser();

// Parse and dispatch a line received on Serial1
void parseLine(const String &line);

#endif // PARSER_H



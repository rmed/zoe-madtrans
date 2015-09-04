#!/usr/bin/env perl
#
# Zoe madtrans
# https://github.com/rmed/zoe-madtrans
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

use Getopt::Long qw(:config pass_through);

my $get;
my $run;
my $bus_calendar;
my $bus_lines;
my $bus_nodes;
my $bus_route;
my $bus_schedule;
my $geo_arrivals;
my $geo_line;
my $geo_stops_from;

my $sender;
my $src;
my @strings;
my @integers;

GetOptions("get"                   => \$get,
           "run"                   => \$run,
           "msg-sender-uniqueid=s" => \$sender,
           "msg-src=s"             => \$src,
           "bc"                    => \$bus_calendar,
           "bl"                    => \$bus_lines,
           "bn"                    => \$bus_nodes,
           "br"                    => \$bus_route,
           "bs"                    => \$bus_schedule,
           "ga"                    => \$geo_arrivals,
           "gi"                    => \$geo_line,
           "gs"                    => \$geo_stops_from,

           "string=s"              => \@strings,
           "integer=i"             => \@integers);

if ($get) {
  &get;
} elsif ($run and $bus_calendar) {
  &bus_calendar;
} elsif ($run and $bus_lines) {
  &bus_lines;
} elsif ($run and $bus_nodes) {
  &bus_nodes;
} elsif ($run and $bus_route) {
  &bus_route;
} elsif ($run and $bus_schedule) {
  &bus_schedule;
} elsif ($run and $geo_arrivals) {
  &geo_arrivals;
} elsif ($run and $geo_line) {
  &geo_line;
} elsif ($run and $geo_stops_from) {
  &geo_stops_from;
}

#
# Commands in the script
#
sub get {
  print("--bc bus calendar from <string> to <string>\n");
  print("--bl /bus line/lines <integer> /on <string>\n");
  print("--bn /bus stop <integer>\n");
  print("--br /bus stops /for line <integer> /on <string>\n");
  print("--bs /bus schedule /for line <integer> /on <string>\n");
  print("--ga wait time /at stop <integer>\n");
  print("--gi info/information /of line <integer> /on <string>\n");
  print("--gs stops in <integer> /meters from /stop <integer>\n");

  print("--bc calendario /de bus/autobús de <string> a <string>\n");
  print("--bl línea/líneas de /bus/autobús <integer> /el <string>\n");
  print("--bn parada /de /bus/autobús <integer>\n");
  print("--br paradas /de /bus/autobús /de línea <integer> /el <string>\n");
  print("--bs horario /bus/autobús /para línea <integer> /el <string>\n");
  print("--ga tiempo /de espera /en parada <integer>\n");
  print("--gi info/información /de /la línea <integer> /el <string>\n");
  print("--gs paradas a <integer> /metros de /la /parada <integer>\n");
}

#
# Get EMT calendar for lines
#
sub bus_calendar {
  print("message dst=madtrans&sender=$sender&src=$src&tag=bus-calendar&sdate=$strings[0]&edate=$strings[1]\n");
}

#
# Get information on given lines
#
sub bus_lines {
  print("message dst=madtrans&sender=$sender&src=$src&tag=bus-list-lines&date=$strings[0]&lines=@integers\n");
}

#
# Get information on stops
#
sub bus_nodes {
  print("message dst=madtrans&sender=$sender&src=$src&tag=bus-nodes-lines&stops=@integers\n");
}

#
# Get stops for a given line
#
sub bus_route {
  print("message dst=madtrans&sender=$sender&src=$src&tag=bus-route-lines&date=$strings[0]&line=$integers[0]\n");
}

#
# Get current schedule for the given line
#
sub bus_schedule {
  print("message dst=madtrans&sender=$sender&src=$src&tag=bus-times-lines&date=$strings[0]&line=$integers[0]\n");
}

#
# Get arrival times for a given stop
#
sub geo_arrivals {
    print("message dst=madtrans&sender=$sender&src=$src&tag=geo-arrive-stop&stop=$integers[0]\n");
}

#
# Get extended information on a given line
#
sub geo_line {
  print("message dst=madtrans&sender=$sender&src=$src&tag=geo-info-line-extended&date=$strings[0]&line=$integers[0]\n");
}

#
# Get the stops in a given radius from another stop
#
sub geo_stops_from {
  print("message dst=madtrans&sender=$sender&src=$src&tag=geo-stops-from-stop&radius=$strings[0]&stop=$integers[1]\n");
}

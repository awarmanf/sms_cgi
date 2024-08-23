#!/usr/bin/perl -wT

#
# sms.cgi
# 

use strict;
use DBI;
use CGI;
use POSIX qw(strftime time);

$CGI::DISABLE_UPLOADS   = 0;
$CGI::POST_MAX          = 1024; # 1KB
 
my $DB   = 'smscgi';
my $HOST = 'localhost';
my $PORT = '3306';
my $USER = 'yudi';
my $PASS = 'r1c0b4n4';
#my $SMSDIR = '/var/tmp/smscgi'; # for testing only
my $SMSDIR = '/var/tmp/sms';
my $TMPFILE;
my @arr;
my $i;

my $cgi = new CGI;

if ( $cgi->param('user') && $cgi->param('pass') && $cgi->param('to') && $cgi->param('txt') ) {
  
  my $user = $cgi->param('user');
  my $pass = $cgi->param('pass');
  my $to   = $cgi->param('to');
  my $txt  = $cgi->param('txt');

  my $dbh = DBI->connect("DBI:mysql:database=$DB;host=$HOST;port=$PORT", "$USER", "$PASS")
               || error($cgi, "Can not connect to database.");

  # cek if user exist and is active
  my $sth = $dbh->prepare("select status from users where user=? and pass=?") 
               || error($cgi, "Database error.");
  $sth->execute($user,$pass);

  my ($status);

  if ($status = $sth->fetchrow_array) {
    if ($status == 'active') {
      # check quota (TODO)

      # save sms to database
      $sth = $dbh->prepare("insert into sms_temp (number,sms) values (?,?)") 
                || error($cgi, "Database error.");
      $sth->execute($to,$txt);

      # write sms
      $TMPFILE = "$SMSDIR/sms.".POSIX::time();
      open (OUT, "> $TMPFILE") || error ($cgi, "Error open file for writing.");

      @arr = split (/,/, $to);
      for ($i=0; $i < @arr; $i++) { 
        print OUT "$arr[$i] $txt\n";
      }
      close OUT;
      success ($cgi);
    } else {
      error ($cgi,"Username $user is not active.");
    }
  } else {
    error ($cgi,"Username $user or password not found.");
  }  
} else {
  error ($cgi,"Query is not complete.");
}

sub success {
  my ($cgi ) = @_;
  print $cgi->header( "text/html" ),
        $cgi->start_html( "SMS sent" ),
        $cgi->h1( "SMS sent"),
        $cgi->end_html;
  exit;
}

sub error {
  my ($cgi, $reason ) = @_;
  print $cgi->header( "text/html" ),
        $cgi->start_html( "Error" ),
        $cgi->h1( "Error" ),
        $cgi->p( "Your request was not procesed because the following error ",
               "occured: " ),
        $cgi->p($cgi->i($reason) ),
        $cgi->end_html;
  exit;
}


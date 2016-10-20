$:.unshift(File.dirname(__FILE__) + '/lib')

require 'aphrael'

run Aphrael::Server

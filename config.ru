$:.unshift(File.dirname(__FILE__) + '/lib')

require 'aphrael'

use Rack::Static, urls: ["/js", "/images"], root: "dist"

run Aphrael::Server

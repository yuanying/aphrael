
require 'sinatra/base'

CONFIG_PATH = ENV['APHRAEL_CONFIG'] || File.join(File.dirname(__FILE__), '..', '..', 'configs', 'config.yml')
Aphrael::Resource.init(Aphrael::Config.new(CONFIG_PATH))

class Aphrael::Server < Sinatra::Base

  set :public_folder, File.join(File.dirname(__FILE__), '..', '..', 'dist')

  configure :production do
    require 'sinatra-xsendfile'
    helpers Sinatra::Xsendfile
    Sinatra::Xsendfile.replace_send_file!
  end

  configure :development do
    require 'sinatra/reloader'
    register Sinatra::Reloader
  end

  get '/' do
    send_file File.join(settings.public_folder, 'index.html')
  end

  get '/api/index' do
    return Aphrael::Resource.config
      .image_dirs
      .map
      .with_index{|e, i| e.delete('path'); e['index'] = i; e }
      .to_json
  end

  get '/api/dirs/:index/*' do |index, path|
    directory = Aphrael::Directory.get(@index, path)
    return directory.children
      .map{|e| e.to_h }
      .to_json
  end

end

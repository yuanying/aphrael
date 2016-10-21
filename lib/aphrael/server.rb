
require 'sinatra/base'

class Aphrael::Server < Sinatra::Base

  set :static, true
  set :public_folder, File.join(File.dirname(__FILE__), '..', '..', 'dist')

  configure do
    CONFIG_PATH = ENV['APHRAEL_CONFIG'] || File.join(File.dirname(__FILE__), '..', '..', 'configs', 'config.yml')
    Aphrael::Resource.init(Aphrael::Config.new(CONFIG_PATH))
  end

  configure :production do
    require 'sinatra-xsendfile'
    helpers Sinatra::Xsendfile
    Sinatra::Xsendfile.replace_send_file!
    set :xsf_header, 'X-Accel-Redirect'
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
      .with_index{|e, i| e = e.dup; e.delete('path'); e['index'] = i; e }
      .to_json
  end

  get '/api/dirs/:index/*' do |index, path|
    index = index.to_i
    directory = Aphrael::Directory.get(index, path)
    return directory.children
      .map{|e| e.to_h }
      .to_json
  end

  get '/api/images/:index/*' do |index, path|
    index = index.to_i
    directory = Aphrael::Directory.get(index, path)
    Aphrael::Image.images(directory)
      .map{|e| e.metadata }
      .to_json
  end

  get '/thumbs/:index/*' do |index, path|
    index = index.to_i
    if Aphrael::Resource.directory?(index, path)
      directory = Aphrael::Directory.get(index, path)
      file = Aphrael::Image.images(directory, 1)[0]
    else
      file = Aphrael::Image.get(index, path)
    end
    if file
      file.create_thumbnail
      send_file file.thumbnail_path.to_s
    else
      status 404
      ''
    end
  end

  get '/images/:index/*' do |index, path|
    index = index.to_i
    image = Aphrael::Image.get(index, path)
    send_file image.real_path.to_s
  end

end


require 'sinatra/base'

class Aphrael::Server < Sinatra::Base

  set :static, false
  # set :public_folder, File.join(File.dirname(__FILE__), '..', '..', 'dist')

  configure do
    CONFIG_PATH = ENV['APHRAEL_CONFIG'] || File.join(File.dirname(__FILE__), '..', '..', 'configs', 'config.yml')
    Aphrael::Resource.init(Aphrael::Config.new(CONFIG_PATH))
  end

  configure :production do
    require 'sinatra/xsendfile'
    helpers Sinatra::Xsendfile
    Sinatra::Xsendfile.replace_send_file!
    set :xsf_header, 'X-Accel-Redirect'
  end

  configure :development do
    require 'sinatra/reloader'
    register Sinatra::Reloader
  end

  helpers do
    def thumbnail_image directory
      if file = directory.images(1)[0]
        return file
      else
        if directory = directory.children[0]
          return thumbnail_image(directory)
        else
          return nil
        end
      end
    end
  end

  get '/' do
    open( File.join(File.dirname(__FILE__), '..', '..', 'dist', 'index.html') ) do |io|
      io.read
    end
  end

  get '/api/index' do
    return Aphrael::Resource.config
      .image_dirs
      .map
      .with_index{|e, i| e = e.dup; e.delete('path'); e['index'] = i; e }
      .to_json
  end

  get '/api/dirs/:index/*' do |index, path|
    path = path.force_encoding(Encoding::UTF_8)
    index = index.to_i
    directory = Aphrael::Directory.get(index, path)
    children = directory.children.map{|e| e.to_h }
    images = directory.images.map{|e| e.metadata }
    return {
      dirs: children,
      images: images,
    }.to_json
  end

  get '/api/thumbs/:index/*' do |index, path|
    path = path.force_encoding(Encoding::UTF_8)
    index = index.to_i
    if Aphrael::Resource.directory?(index, path)
      directory = Aphrael::Directory.get(index, path)
      file = thumbnail_image(directory)
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

  get '/api/image/:index/*' do |index, path|
    path = path.force_encoding(Encoding::UTF_8)
    index = index.to_i
    image = Aphrael::Image.get(index, path)
    send_file image.real_path.to_s
  end

  get '/api/movie/:index/*' do |index, path|
    path = path.force_encoding(Encoding::UTF_8)
    index = index.to_i
    image = Aphrael::Image.get(index, path)
    send_file image.movie_real_path.to_s
  end

end

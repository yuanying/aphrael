require 'image_science'
require 'fastimage'

class Aphrael::Image < Aphrael::Resource

  SUPPORTED_FORMATS = ['.png', '.PNG', '.jpg', '.JPG', '.jpeg']

  def self.images directory, length=nil
    images = []
    real_path = directory.real_path

    Dir.foreach(real_path) do |file|
      next if file.start_with?('.')
      if length && images.size >= length
        break
      end
      real_file_path = File.join(real_path, file)
      if File.file?(real_file_path) && SUPPORTED_FORMATS.include?(File.extname(real_file_path))
        images << self.get(directory.index, File.join(directory.path, file))
      end
    end
    return images.sort
  end

  def self.get index, path
    @cache ||= {}
    real_path = Aphrael::Resource.real_path(index, path)
    unless image = @cache[real_path]
      image = Aphrael::Image.new(index, path)
    end
    image
  end

  def initialize index, path
    super
    create_metadata
  end

  attr_reader :metadata

  def create_metadata
    if File.exist?(metadata_path)
      open(metadata_path) do |io|
        @metadata = JSON.parse(io.read)
      end
      return
    end
    FileUtils.mkdir_p(File.dirname(metadata_path)) unless File.exist?(File.dirname(metadata_path))

    size = ::FastImage.size(self.real_path)
    @metadata = {
      path: self.path,
      w: size[0],
      h: size[1],
    }
    open(metadata_path, 'w') do |io|
      io.write(@metadata.to_json)
    end
  rescue
    puts self.path
  end

  def create_thumbnail
    return if File.exist?(thumbnail_path)

    FileUtils.mkdir_p(File.dirname(thumbnail_path)) unless File.exist?(File.dirname(thumbnail_path))

    ImageScience.with_image(self.real_path) do |img|
      img.cropped_thumbnail(128) do |thumb|
        thumb.save thumbnail_path
      end
    end
  rescue
    puts "Cannot create thumbnail: #{path}"
  end

  def thumbnail_path
    File.join(Aphrael::Resource.tmp_dir, 'thumb', real_path)
  end

  def metadata_path
    File.join(Aphrael::Resource.tmp_dir, 'meta', "#{real_path}.json")
  end

end

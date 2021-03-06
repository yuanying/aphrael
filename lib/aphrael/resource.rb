
class Aphrael::Resource
  def self.init config
    @@config = config
  end

  def self.config
    @@config
  end

  def self.directory? index, path
    File.directory?(self.real_path(index, path))
  end

  def self.real_path index, path
    File.join(self.image_dir(index), path)
  end

  def self.static_dir
    self.config.static_dir || File.join(File.dirname(__FILE__), '..', 'public')
  end

  def self.tmp_dir
    self.config.tmp_dir
  end

  def self.image_dir index
    File.expand_path(self.config.image_dirs[index]['path'])
  end

  def initialize index, path
    @path   = path
    @index  = index.to_i
    raise if File.expand_path(real_path).length < self.class.image_dir(index).length
  end

  attr_accessor :path
  attr_accessor :index

  def real_path
    self.class.real_path(index, path)
  end

  def name
    File.basename(path)
  end

  def <=>(other)
    self.name <=> other.name
  end

  def ==(other)
    self.path == other.path
  end
end

# require 'image'
# require 'directory'

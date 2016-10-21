require 'uri'

class Aphrael::Directory < Aphrael::Resource

  def self.get index, path
    @cache ||= {}
    index = index.to_i
    real_path = self.real_path(index, path)
    unless directory = @cache[real_path]
      directory = self.new(index, path)
    end
    directory
  end

  def initialize index, path
    super
  end

  def children
    create_index
    @children
  end

  def create_index
    unless defined?(@children)
      @children = []
      Dir.entries(real_path).sort.each do |file|
        next if file.start_with?('.')
        real_file_path = File.join(real_path, file)
        if File.directory?(real_file_path)
          _path = [path, file]
          _path.delete('')
          @children << self.class.get(index, File.join(*_path))
        end
      end
    end
    @children
  end

  def to_h
    return {
      path: URI.escape(path),
      name: URI.escape(File.basename(path)),
    }
  end

end

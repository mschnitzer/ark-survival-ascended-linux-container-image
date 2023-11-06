module AsaCtrl
  module StartParamsHelper
    def self.get_value(start_params, key)
      return unless start_params

      value = ''
      offset = start_params.index("#{key}=")

      return unless offset

      offset += "#{key}=".length

      start_params[offset..-1].each_char do |char|
        break if char == ' ' || char == '?'

        value += char
      end

      value
    end
  end
end

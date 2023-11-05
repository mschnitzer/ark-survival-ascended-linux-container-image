module AsaCtrl
  module Cli
    class CliInterface
      def initialize(opts)
        @opts = opts

        print_help! if opts[:help]
      end

      def print_help!
        raise "Help not implemented!"
      end
    end
  end
end

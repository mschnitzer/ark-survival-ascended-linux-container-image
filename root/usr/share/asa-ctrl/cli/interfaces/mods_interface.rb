module AsaCtrl
  module Cli
    class ModsInterface < CliInterface
      def initialize(opts)
        super(opts)

        execute!
      end

      def execute!
        exit! 0
      end

      def print_help!
        puts "Usage: asa-ctrl mods (--install)"
        exit! 0
      end
    end
  end
end

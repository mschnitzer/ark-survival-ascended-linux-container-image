module AsaCtrl
  module Cli
    HELP_ARGUMENT = '--help'
    HELP_DESCRIPTION = 'Prints a help message'

    def self.passed_command(args)
      if ARGV.size == 0
        []
      else
        [ARGV[0]]
      end
    end

    def self.print_usage
      puts "Usage: asa-ctrl [mods] (--help)"
    end
  end
end

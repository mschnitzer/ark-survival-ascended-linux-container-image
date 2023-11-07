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
      puts "Usage: asa-ctrl [rcon|mods] (--help)"
    end

    def self.exit_with_error!(message, code)
      $stderr.puts "Error: #{message}"
      exit! code
    end
  end
end

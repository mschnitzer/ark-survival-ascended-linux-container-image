module AsaCtrl
  module Cli
    class RconInterface < CliInterface
      def initialize(opts)
        super(opts)

        execute!
      end

      def execute!
        if @opts[:exec]
          run_command!
        end

        exit! AsaCtrl::ExitCodes::OK
      end

      def run_command!
        rcon_command = @opts[:exec]
        response = AsaCtrl::Rcon.exec_command!('127.0.0.1', AsaCtrl::Rcon.identify_port, rcon_command, AsaCtrl::Rcon.identify_password)

        if response[:id] == AsaCtrl::Rcon::PacketTypes::RESPONSE_VALUE
          puts response[:body]
        else
          AsaCtrl::Cli.exit_with_error!("Rcon command execution failed: #{response}",
            AsaCtrl::ExitCodes::RCON_COMMAND_EXECUTION_FAILED)
        end
      rescue AsaCtrl::Errors::RconPasswordNotFoundError
        AsaCtrl::Cli.exit_with_error!("Could not read RCON password. Make sure it is properly configured, either as start parameter ?ServerAdminPassword=mypass or " \
          "in GameUserSettings.ini in the [ServerSettings] section as ServerAdminPassword=mypass", AsaCtrl::ExitCodes::RCON_PASSWORD_NOT_FOUND)
      rescue AsaCtrl::Errors::RconAuthenticationError
        AsaCtrl::Cli.exit_with_error!("Could not execute this RCON command. Authentication failed (wrong server password).",
          AsaCtrl::ExitCodes::RCON_PASSWORD_WRONG)
      end

      def print_help!
        puts "Usage: asa-ctrl rcon [--exec]"
        exit! AsaCtrl::ExitCodes::OK
      end
    end
  end
end

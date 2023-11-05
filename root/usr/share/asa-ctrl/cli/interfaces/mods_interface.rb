module AsaCtrl
  module Cli
    class ModsInterface < CliInterface
      def initialize(opts)
        super(opts)

        execute!
      end

      def execute!
        if @opts[:enable]
          enable_mod!
        end

        exit! AsaCtrl::ExitCodes::OK
      end

      def enable_mod!
        mod_id = @opts[:enable]
        AsaCtrl::Mods::Database.get_instance.enable_mod!(mod_id)

        puts "Enabled mod id '#{mod_id}' successfully. The server will download the mod upon startup."
      rescue AsaCtrl::Errors::ModAlreadyEnabledError
        AsaCtrl::Cli.exit_with_error!("This mod is already enabled! Use 'asa-ctrl mods --list' to see what mods are currently enabled.",
          AsaCtrl::ExitCodes::MOD_ALREADY_ENABLED)
      end

      def print_help!
        puts "Usage: asa-ctrl mods [--install] (--dry-run)"
        exit! AsaCtrl::ExitCodes::OK
      end
    end
  end
end

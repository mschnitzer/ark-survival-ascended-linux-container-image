module AsaCtrl
  module Mods
    MOD_DATABASE_PATH = '/home/gameserver/server-files/mods.json'

    class Database
      @@singleton_reference = nil

      def initialize(database_path)
        @database_path = database_path

        ensure_database_presence!
        load_database
      end

      def self.get_instance
        return @@singleton_reference if @@singleton_reference
        @@singleton_reference = Database.new(MOD_DATABASE_PATH)
      end

      def enable_mod!(mod_id)
        @database.each do |record|
          if record['mod_id'].to_i == mod_id.to_i
            raise AsaCtrl::Errors::ModAlreadyEnabledError if record['enabled']

            record['enabled'] = true
            write_database!

            return
          end
        end

        add_new_record!(mod_id, 'unknown', true, false)
      end

      def add_new_record!(mod_id, name, enabled, scanned)
        @database << {
          mod_id: mod_id.to_i,
          name: name,
          enabled: enabled,
          scanned: scanned
        }

        write_database!
      end

      def write_database!
        File.write(@database_path, JSON.pretty_generate(@database))
      end

      def ensure_database_presence!
        return if File.exist?(@database_path)

        @database = []
        write_database!
      end

      def load_database
        @database = JSON.parse(File.read(@database_path))
      rescue JSON::ParserError
        # we do not want to delete the file for the user, as they might want to save its content first
        AsaCtrl::Cli.exit_with_error!("mods.json file is corrupted and cannot be parsed, please delete this file " \
          "manually. It can be found in the server files root directory.", AsaCtrl::ExitCodes::CORRUPTED_MODS_DATABASE)
      end
    end
  end
end

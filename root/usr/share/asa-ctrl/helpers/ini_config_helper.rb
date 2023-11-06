module AsaCtrl
  module IniConfigHelper
    def self.game_user_settings_ini
      self.parse('/home/gameserver/server-files/ShooterGame/Saved/Config/WindowsServer/GameUserSettings.ini')
    end

    def self.game_ini
      self.parse('/home/gameserver/server-files/ShooterGame/Saved/Config/WindowsServer/Game.ini')
    end

    def self.parse(path)
      return unless File.exist?(path)

      IniParse.parse(File.read(path))
    end
  end
end

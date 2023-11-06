module AsaCtrl
  module Rcon
    module PacketTypes
      RESPONSE_VALUE = 0
      EXEC_COMMAND = 2
      AUTH_RESPONSE = 2
      AUTH = 3
    end

    Packet = Struct.new(:size, :id, :type, :body)

    def self.exec_command!(server_ip, rcon_port, rcon_command, password)
      socket = TCPSocket.new(server_ip, rcon_port)
      raise AsaCtrl::Errors::RconAuthenticationError unless self.authenticate!(socket, password)

      self.send_packet!(socket, rcon_command, PacketTypes::EXEC_COMMAND)
    end

    def self.authenticate!(socket, password)
      response = self.send_packet!(socket, password, PacketTypes::AUTH)
      response[:id] != -1
    end

    def self.send_packet!(socket, data, packet_id)
      packet = Packet.new(10+data.bytesize, 0, packet_id, data)

      self.send_to(packet, socket)
      self.recv_from(socket)
    end

    def self.send_to(packet, socket)
      szb = [packet[:size]].pack 'l<'
      idb = [packet[:id]].pack 'l<'
      type_b = [packet[:type]].pack 'l<'
      body_b = [packet[:body]].pack 'Z*'
      data = szb + idb + type_b + body_b + "\0"
  
      socket.sendmsg(data)
    end
  
    def self.recv_from(socket)
      msg_ary = socket.recvmsg
      msg = msg_ary[0]
      ary = msg.unpack('l<l<l<Z*')
  
      Packet.new(ary[0], ary[1], ary[2], ary[3])
    end

    def self.identify_password
      password = AsaCtrl::StartParamsHelper.get_value(ENV['ASA_START_PARAMS'], 'ServerAdminPassword')
      return password if password

      config = AsaCtrl::IniConfigHelper.game_user_settings_ini
      return config['ServerSettings']['ServerAdminPassword'] if config['ServerSettings'] && config['ServerSettings']['ServerAdminPassword']

      raise AsaCtrl::Errors::RconPasswordNotFoundError
    end

    def self.identify_port
      port = AsaCtrl::StartParamsHelper.get_value(ENV['ASA_START_PARAMS'], 'RCONPort')
      return port.to_i if port

      config = AsaCtrl::IniConfigHelper.game_user_settings_ini
      return config['ServerSettings']['RCONPort'].to_i if config['ServerSettings'] && config['ServerSettings']['RCONPort']

      raise AsaCtrl::Errors::RconPortNotFoundError
    end
  end
end

#!/usr/bin/ruby.ruby3.3
require 'json'
require 'slop'
require 'iniparse'
require 'socket'

if ENV['DEV'] == '1'
  require 'byebug'
end

require_relative './exit_codes.rb'
require_relative './errors/errors.rb'
require_relative './helpers/helpers.rb'
require_relative './mods/database.rb'
require_relative './rcon/rcon.rb'
require_relative './cli/utils.rb'
require_relative './cli/interfaces/cli_interface.rb'
require_relative './cli/interfaces/mods_interface.rb'
require_relative './cli/interfaces/rcon_interface.rb'

main_args = Slop.parse(AsaCtrl::Cli.passed_command(ARGV)) do |args|
  args.on 'rcon', 'Interface for RCON command execution' do
    opts = Slop.parse(ARGV[1..-1]) do |opt|
      opt.string '--exec', 'An RCON command to execute'
      opt.bool AsaCtrl::Cli::HELP_ARGUMENT, AsaCtrl::Cli::HELP_DESCRIPTION
    end

    AsaCtrl::Cli::RconInterface.new(opts)
  end

  args.on 'mods', 'Interface to manage mods' do
    opts = Slop.parse(ARGV[1..-1]) do |opt|
      opt.integer '--enable', 'Mod ID/CurseForge Project ID of the mod'
      opt.bool AsaCtrl::Cli::HELP_ARGUMENT, AsaCtrl::Cli::HELP_DESCRIPTION
    end

    AsaCtrl::Cli::ModsInterface.new(opts)
  end

  args.on AsaCtrl::Cli::HELP_ARGUMENT, AsaCtrl::Cli::HELP_DESCRIPTION do
    # handled once slop exits
  end
end

AsaCtrl::Cli.print_usage

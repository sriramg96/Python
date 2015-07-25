    def __init__(self, virtapi, read_only=False):
        super(vmanDriver, self).__init__(virtapi)

        global vman
        if vman is None:
            vman = importutils.import_module('vman')

        self._host = host.Host(self._uri(), read_only,
                               lifecycle_event_handler=self.emit_event,
                               conn_event_handler=self._handle_conn_event)
        self._initiator = None
        self._fc_wwnns = None
        self._fc_wwpns = None
        self._caps = None
        self.firewall_driver = firewall.load_driver(
            DEFAULT_FIREWALL_DRIVER,
            self.virtapi,
            host=self._host)

        self.vif_driver = vman_vif.vmanGenericVIFDriver()

        self.volume_drivers = driver.driver_dict_from_config(
            self._get_volume_drivers(), self)

        self._disk_cachemode = None
        self.image_cache_manager = imagecache.ImageCacheManager()
        self.image_backend = imagebackend.Backend(CONF.use_cow_images)

        self.disk_cachemodes = {}

        self.valid_cachemodes = ["default",
                                 "none",
                                 "writethrough",
                                 "writeback",
                                 "directsync",
                                 "unsafe",
                                ]
        self._conn_supports_start_paused = CONF.vman.virt_type in ('kvm',
                                                                      'qemu')

        for mode_str in CONF.vman.disk_cachemodes:
            disk_type, sep, cache_mode = mode_str.partition('=')
            if cache_mode not in self.valid_cachemodes:
                LOG.warn(_LW('Invalid cachemode %(cache_mode)s specified '
                             'for disk type %(disk_type)s.'),
                         {'cache_mode': cache_mode, 'disk_type': disk_type})
                continue
            self.disk_cachemodes[disk_type] = cache_mode

        self._volume_api = volume.API()
        self._image_api = image.API()

        sysinfo_serial_funcs = {
            'none': lambda: None,
            'hardware': self._get_host_sysinfo_serial_hardware,
            'os': self._get_host_sysinfo_serial_os,
            'auto': self._get_host_sysinfo_serial_auto,
        }

        self._sysinfo_serial_func = sysinfo_serial_funcs.get(
            CONF.vman.sysinfo_serial)
        if not self._sysinfo_serial_func:
            raise exception.NovaException(
                _("Unexpected sysinfo_serial setting '%(actual)s'. "
                  "Permitted values are %(expect)s'") %
                  {'actual': CONF.vman.sysinfo_serial,
                   'expect': ', '.join("'%s'" % k for k in
                                       sysinfo_serial_funcs.keys())})

def _destroy(self, instance, attempt=1):
        try:
            guest = self._host.get_guest(instance)
        except exception.InstanceNotFound:
            guest = None

        # If the instance is already terminated, we're still happy
        # Otherwise, destroy it
        old_domid = -1
        if guest is not None:
            try:
                old_domid = guest.id
                guest.poweroff()
                
            except vman.vmanError as e:
                is_okay = False
                errcode = e.get_error_code()
                if errcode == vman.VIR_ERR_NO_DOMAIN:
                    # Domain already gone. This can safely be ignored.
                    is_okay = True
                elif errcode == vman.VIR_ERR_OPERATION_INVALID:
                    # If the instance is already shut off, we get this:
                    # Code=55 Error=Requested operation is not valid:
                    # domain is not running

                    # TODO(sahid): At this point we should be a Guest object
                    state = self._get_power_state(guest._domain)
                    if state == power_state.SHUTDOWN:
                        is_okay = True
                elif errcode == vman.VIR_ERR_INTERNAL_ERROR:
                    errmsg = e.get_error_message()
                    if (CONF.vman.virt_type == 'lxc' and
                        errmsg == 'internal error: '
                                  'Some processes refused to die'):
                        # Some processes in the container didn't die
                        # fast enough for vman. The container will
                        # eventually die. For now, move on and let
                        # the wait_for_destroy logic take over.
                        is_okay = True
               elif errcode == vman.VIR_ERR_OPERATION_TIMEOUT:
                    LOG.warn(_LW("Cannot destroy instance, operation time "
                                 "out"),
                            instance=instance)
                    reason = _("operation time out")
                    raise exception.InstancePowerOffFailure(reason=reason)
                elif errcode == vman.VIR_ERR_SYSTEM_ERROR:
                    if e.get_int1() == errno.EBUSY:
                        # NOTE(danpb): When vman kills a process it sends it
                        # SIGTERM first and waits 10 seconds. If it hasn't gone
                        # it sends SIGKILL and waits another 5 seconds. If it
                        # still hasn't gone then you get this EBUSY error.
                        # Usually when a QEMU process fails to go away upon
                        # SIGKILL it is because it is stuck in an
                        # uninterruptable kernel sleep waiting on I/O from
                        # some non-responsive server.
                        # Given the CPU load of the gate tests though, it is
                        # conceivable that the 15 second timeout is too short,
                        # particularly if the VM running tempest has a high
                        # steal time from the cloud host. ie 15 wallclock
                        # seconds may have passed, but the VM might have only
                        # have a few seconds of scheduled run time.
                       LOG.warn(_LW('Error from vman during destroy. '
                                     'Code=%(errcode)s Error=%(e)s; '
                                     'attempt %(attempt)d of 3'),
                                 {'errcode': errcode, 'e': e,
                                  'attempt': attempt},
                                 instance=instance)
                        with excutils.save_and_reraise_exception() as ctxt:
                            # Try up to 3 times before giving up.
                            if attempt < 3:
                                ctxt.reraise = False
                                self._destroy(instance, attempt + 1)
                                return

                if not is_okay:
                    with excutils.save_and_reraise_exception():
                        LOG.error(_LE('Error from vman during destroy. '
                                      'Code=%(errcode)s Error=%(e)s'),
                                  {'errcode': errcode, 'e': e},
                                  instance=instance)
                                  
        def _wait_for_destroy(expected_domid):
            """Called at an interval until the VM is gone."""
            # NOTE(vish): If the instance disappears during the destroy
            #             we ignore it so the cleanup can still be
            #             attempted because we would prefer destroy to
            #             never fail.
            try:
                dom_info = self.get_info(instance)
                state = dom_info.state
                new_domid = dom_info.id
            except exception.InstanceNotFound:
                LOG.info(_LI("During wait destroy, instance disappeared."),
                         instance=instance)
                raise loopingcall.LoopingCallDone()

            if state == power_state.SHUTDOWN:
                LOG.info(_LI("Instance destroyed successfully."),
                         instance=instance)
                raise loopingcall.LoopingCallDone()

            # NOTE(wangpan): If the instance was booted again after destroy,
            #                this may be a endless loop, so check the id of
            #                domain here, if it changed and the instance is
            #                still running, we should destroy it again.
            # see https://bugs.launchpad.net/nova/+bug/1111213 for more details
            if new_domid != expected_domid:
                LOG.info(_LI("Instance may be started again."),
                         instance=instance)
                kwargs['is_running'] = True
                raise loopingcall.LoopingCallDone()

        kwargs = {'is_running': False}
        timer = loopingcall.FixedIntervalLoopingCall(_wait_for_destroy,
                                                     old_domid)
        timer.start(interval=0.5).wait()
        if kwargs['is_running']:
            LOG.info(_LI("Going to destroy instance again."),
                     instance=instance)
            self._destroy(instance)
        else:
            # NOTE(GuanQiang): teardown container to avoid resource leak
            if CONF.vman.virt_type == 'lxc':
                self._teardown_container(instance)            

    def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):
        self._destroy(instance)
        self.cleanup(context, instance, network_info, block_device_info,
                     destroy_disks, migrate_data)

def spawn(self, context, instance, image_meta, injected_files,
              admin_password, network_info=None, block_device_info=None):
        disk_info = blockinfo.get_disk_info(CONF.vman.virt_type,
                                            instance,
                                            image_meta,
                                            block_device_info)
        self._create_image(context, instance,
                           disk_info['mapping'],
                           network_info=network_info,
                           block_device_info=block_device_info,
                           files=injected_files,
                           admin_pass=admin_password)
        xml = self._get_guest_xml(context, instance, network_info,
                                  disk_info, image_meta,
                                  block_device_info=block_device_info,
                                  write_to_disk=True)
        self._create_domain_and_network(context, xml, instance, network_info,
                                        disk_info,
                                        block_device_info=block_device_info)
        LOG.debug("Instance is running", instance=instance)

        def _wait_for_boot():
            """Called at an interval until the VM is running."""
            state = self.get_info(instance).state

            if state == power_state.RUNNING:
                LOG.info(_LI("Instance spawned successfully."),
                         instance=instance)
                raise loopingcall.LoopingCallDone()

        timer = loopingcall.FixedIntervalLoopingCall(_wait_for_boot)
        timer.start(interval=0.5).wait()

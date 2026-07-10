try {
  (() => {
    const app = __$$hmAppManager$$__.currentApp;

    app.__globals__ = {
      lang: new DeviceRuntimeCore.HmUtils.Lang(
        DeviceRuntimeCore.HmUtils.getLanguage()
      ),
      px: DeviceRuntimeCore.HmUtils.getPx(212)
    };

    app.app = DeviceRuntimeCore.App({
      globalData: {},
      onCreate() {},
      onDestroy() {},
      onError(error) {
        console.log('TIME FLIES app error', error);
      }
    });
  })();
} catch (error) {
  console.log('TIME FLIES bootstrap error', error);
}

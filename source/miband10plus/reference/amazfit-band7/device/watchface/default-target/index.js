try {
    (() => {
        const __$$app$$__ = __$$hmAppManager$$__.currentApp;
        function getApp() {
            return __$$app$$__.app;
        }
        function getCurrentPage() {
            return __$$app$$__.current && __$$app$$__.current.module;
        }
        const __$$module$$__ = __$$app$$__.current;
        const h = new DeviceRuntimeCore.WidgetFactory(new DeviceRuntimeCore.HmDomApi(__$$app$$__, __$$module$$__));
        const {px} = __$$app$$__.__globals__;
        let normal$_$lunar$_$festival_or_solar_term = '';
        let timeSensor = '';
        let lunar_month = '';
        let festival = '';
        const logger = Logger.getLogger('watchface6');
        __$$module$$__.module = DeviceRuntimeCore.WatchFace({
            init_view() {
                normal$_$lunar$_$festival_or_solar_term = hmUI.createWidget(hmUI.widget.TEXT, {
                    x: 57,
                    y: 308,
                    w: 77,
                    h: 22,
                    text: '',
                    color: '0xFFd5d4d4',
                    text_size: 17,
                    align_h: hmUI.align.CENTER_H,
                    align_v: hmUI.align.CENTER_V,
                    show_level: hmUI.show_level.ONLY_NORMAL
                });
                timeSensor = hmSensor.createSensor(hmSensor.id.TIME);
                function isVoid(value) {
                    return value === 'INVALID';
                }
                function getLunarText() {
                    lunar_month = timeSensor.lunar_month;
                    timeSensor.lunar_day;
                    festival = timeSensor.getShowFestival();
                    festival = isVoid(festival) ? '' : festival;
                    if (!isVoid(lunar_month)) {
                        if (lunar_month.indexOf('闰') > -1);
                    }
                    normal$_$lunar$_$festival_or_solar_term.setProperty(hmUI.prop.MORE, { text: festival });
                }
                hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE, {
                    resume_call: function () {
                        getLunarText();
                    }
                });
            },
            onInit() {
                logger.log('index page.js on init invoke');
            },
            build() {
                this.init_view();
                logger.log('index page.js on ready invoke');
            },
            onDestroy() {
                logger.log('index page.js on destroy invoke');
            }
        });
        ;
    })();
} catch (e) {
    console.log('Mini Program Error', e);
    e && e.stack && e.stack.split(/\n/).forEach(i => console.log('error stack', i));
    ;
}

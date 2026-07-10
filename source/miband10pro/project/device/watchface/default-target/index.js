try {
  (() => {
    const app = __$$hmAppManager$$__.currentApp;
    const module = app.current;
    const logger = Logger.getLogger('time-flies-band10-pro');

    const SCREEN_WIDTH = 400;
    const SCREEN_HEIGHT = 480;
    const PANEL_X = 198;
    const PANEL_PADDING = 22;
    const ASSET_ROOT = 'assets/';

    const TIME_DIGITS = Array.from(
      { length: 10 },
      (_, value) => `${ASSET_ROOT}time/${value}.png`
    );
    const WEEK_IMAGES = Array.from(
      { length: 7 },
      (_, index) => `${ASSET_ROOT}week/${index + 1}.png`
    );
    const BATTERY_IMAGES = Array.from(
      { length: 10 },
      (_, value) => `${ASSET_ROOT}battery/${value}.png`
    );

    let timeSensor;
    let stepSensor;
    let heartSensor;
    let batterySensor;

    let hourTensImage;
    let hourOnesImage;
    let minuteTensImage;
    let minuteOnesImage;
    let weekImage;
    let batteryImage;

    let dateText;
    let stepsText;
    let heartText;
    let batteryText;
    let festivalText;

    function pad2(value) {
      const number = Number(value);
      return number < 10 ? `0${number}` : `${number}`;
    }

    function setText(widget, text) {
      if (!widget) return;
      widget.setProperty(hmUI.prop.MORE, { text });
    }

    function setImage(widget, src) {
      if (!widget || !src) return;
      widget.setProperty(hmUI.prop.MORE, { src });
    }

    function safeNumber(value, fallback = '--', allowZero = true) {
      const number = Number(value);
      if (!Number.isFinite(number)) return fallback;
      if (allowZero ? number < 0 : number <= 0) return fallback;
      return `${Math.round(number)}`;
    }

    function updateClock() {
      if (!timeSensor) return;

      const hour = pad2(timeSensor.hour);
      const minute = pad2(timeSensor.minute);

      setImage(hourTensImage, TIME_DIGITS[Number(hour[0])]);
      setImage(hourOnesImage, TIME_DIGITS[Number(hour[1])]);
      setImage(minuteTensImage, TIME_DIGITS[Number(minute[0])]);
      setImage(minuteOnesImage, TIME_DIGITS[Number(minute[1])]);

      setText(
        dateText,
        `${timeSensor.year}.${pad2(timeSensor.month)}.${pad2(timeSensor.day)}`
      );

      const weekIndex = Math.max(1, Math.min(7, Number(timeSensor.week))) - 1;
      setImage(weekImage, WEEK_IMAGES[weekIndex]);
    }

    function updateSteps() {
      if (!stepSensor) return;
      setText(stepsText, safeNumber(stepSensor.current, '0', true));
    }

    function updateHeart() {
      if (!heartSensor) return;
      setText(heartText, safeNumber(heartSensor.last, '--', false));
    }

    function updateBattery() {
      if (!batterySensor) return;

      const current = Math.max(0, Math.min(100, Number(batterySensor.current) || 0));
      const imageIndex = Math.min(9, Math.floor(current / 10));
      setImage(batteryImage, BATTERY_IMAGES[imageIndex]);
      setText(batteryText, `${Math.round(current)}%`);
    }

    function updateFestival() {
      if (!timeSensor) return;
      const festival = timeSensor.getShowFestival();
      setText(festivalText, festival === 'INVALID' ? '' : festival);
    }

    function refreshAll() {
      updateClock();
      updateSteps();
      updateHeart();
      updateBattery();
      updateFestival();
    }

    const minuteListener = function () {
      updateClock();
      updateFestival();
    };
    const stepListener = function () {
      updateSteps();
    };
    const heartListener = function () {
      updateHeart();
    };
    const batteryListener = function () {
      updateBattery();
    };

    module.module = DeviceRuntimeCore.WatchFace({
      initView() {
        hmUI.createWidget(hmUI.widget.FILL_RECT, {
          x: 0,
          y: 0,
          w: SCREEN_WIDTH,
          h: SCREEN_HEIGHT,
          color: '0xFF000000',
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.IMG, {
          x: 0,
          y: 0,
          src: `${ASSET_ROOT}bg/bg.png`,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.FILL_RECT, {
          x: PANEL_X,
          y: 0,
          w: SCREEN_WIDTH - PANEL_X,
          h: SCREEN_HEIGHT,
          color: '0xFF05070A',
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.FILL_RECT, {
          x: PANEL_X,
          y: 24,
          w: 1,
          h: SCREEN_HEIGHT - 48,
          color: '0xFF464646',
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hourTensImage = hmUI.createWidget(hmUI.widget.IMG, {
          x: 28,
          y: 150,
          src: TIME_DIGITS[0],
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        hourOnesImage = hmUI.createWidget(hmUI.widget.IMG, {
          x: 96,
          y: 150,
          src: TIME_DIGITS[0],
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        minuteTensImage = hmUI.createWidget(hmUI.widget.IMG, {
          x: 28,
          y: 254,
          src: TIME_DIGITS[0],
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        minuteOnesImage = hmUI.createWidget(hmUI.widget.IMG, {
          x: 96,
          y: 254,
          src: TIME_DIGITS[0],
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING,
          y: 20,
          w: 160,
          h: 32,
          text: 'TIME FLIES',
          color: '0xFFFFFFFF',
          text_size: 20,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        dateText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING,
          y: 62,
          w: 160,
          h: 28,
          text: '----.--.--',
          color: '0xFFD7D7D7',
          text_size: 18,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        weekImage = hmUI.createWidget(hmUI.widget.IMG, {
          x: PANEL_X + PANEL_PADDING,
          y: 100,
          src: WEEK_IMAGES[0],
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING,
          y: 146,
          w: 160,
          h: 24,
          text: 'STEPS',
          color: '0xFF777777',
          text_size: 14,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        stepsText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING,
          y: 170,
          w: 160,
          h: 42,
          text: '0',
          color: '0xFFFFFFFF',
          text_size: 30,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING,
          y: 232,
          w: 160,
          h: 24,
          text: 'HEART',
          color: '0xFF777777',
          text_size: 14,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        heartText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING,
          y: 256,
          w: 160,
          h: 42,
          text: '--',
          color: '0xFFFFFFFF',
          text_size: 30,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING,
          y: 318,
          w: 160,
          h: 24,
          text: 'BATTERY',
          color: '0xFF777777',
          text_size: 14,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        batteryImage = hmUI.createWidget(hmUI.widget.IMG, {
          x: PANEL_X + PANEL_PADDING,
          y: 352,
          src: BATTERY_IMAGES[0],
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        batteryText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING + 60,
          y: 344,
          w: 92,
          h: 40,
          text: '--%',
          color: '0xFFFFFFFF',
          text_size: 22,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        festivalText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: PANEL_X + PANEL_PADDING,
          y: 414,
          w: 160,
          h: 32,
          text: '',
          color: '0xFFD5D4D4',
          text_size: 18,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        timeSensor = hmSensor.createSensor(hmSensor.id.TIME);
        stepSensor = hmSensor.createSensor(hmSensor.id.STEP);
        heartSensor = hmSensor.createSensor(hmSensor.id.HEART);
        batterySensor = hmSensor.createSensor(hmSensor.id.BATTERY);

        timeSensor.addEventListener(timeSensor.event.MINUTEEND, minuteListener);
        stepSensor.addEventListener(hmSensor.event.CHANGE, stepListener);
        heartSensor.addEventListener(heartSensor.event.LAST, heartListener);
        batterySensor.addEventListener(hmSensor.event.CHANGE, batteryListener);

        hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE, {
          resume_call() {
            refreshAll();
          }
        });

        refreshAll();
      },

      onInit() {
        logger.log(`provisional target canvas ${SCREEN_WIDTH}x${SCREEN_HEIGHT}`);
      },

      build() {
        this.initView();
      },

      onDestroy() {
        if (timeSensor) {
          timeSensor.removeEventListener(timeSensor.event.MINUTEEND, minuteListener);
        }
        if (stepSensor) {
          stepSensor.removeEventListener(hmSensor.event.CHANGE, stepListener);
        }
        if (heartSensor) {
          heartSensor.removeEventListener(heartSensor.event.LAST, heartListener);
        }
        if (batterySensor) {
          batterySensor.removeEventListener(hmSensor.event.CHANGE, batteryListener);
        }
        logger.log('TIME FLIES Band 10 Pro watchface destroyed');
      }
    });
  })();
} catch (error) {
  console.log('TIME FLIES Band 10 Pro watchface error', error);
}

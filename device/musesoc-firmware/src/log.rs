//! A simple logger for the `log` crate which can log to any object
//! implementing `Write`

#![allow(unused_imports, unused_mut, unused_variables)]

use crate::{hal, pac};

use log::{Level, LevelFilter, Metadata, Record};

use core::cell::RefCell;
use core::fmt::Write;

// - initialization -----------------------------------------------------------

static LOGGER: WriteLogger<hal::Serial> = WriteLogger {
    writer: RefCell::new(None),
    level: Level::Trace,
};

pub fn init(writer: hal::Serial) {
    LOGGER.writer.replace(Some(writer));

    // TODO we need support for atomics to use log::set_logger()
    unsafe { log::set_logger_racy(&LOGGER) }
        .map(|()| log::set_max_level(LevelFilter::Trace))
        .unwrap();
}

// - implementation -----------------------------------------------------------

/// WriteLogger
pub struct WriteLogger<W>
where
    W: Write + Send,
{
    pub writer: RefCell<Option<W>>,
    pub level: Level,
}

impl<W> log::Log for WriteLogger<W>
where
    W: Write + Send,
{
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= self.level
    }

    fn log(&self, record: &Record) {
        riscv::interrupt::free(|| match self.writer.borrow_mut().as_mut() {
            Some(writer) => {
                writeln!(writer, "{} - {}", record.level(), record.args())
                    .expect("Logger failed to write to device");
            }
            None => {
                panic!("Logger has not been initialized");
            }
        })
    }

    fn flush(&self) {}
}

// TODO add support for critical-section crate
// TODO implement a riscv::interrupt::Mutex
unsafe impl<W: Write + Send> Sync for WriteLogger<W> {}

// - format! ------------------------------------------------------------------

/// format! macro for no_std, no alloc environments
///
/// Props: https://stackoverflow.com/questions/50200268/
/// Props: https://github.com/Simsys/arrform
///
/// TODO Re-use buffer

#[cfg(not(feature = "alloc"))]
pub mod format_nostd {
    pub const SIZE: usize = 80;

    #[macro_export]
    macro_rules! _format {
        ($($arg:tt)*) => {
            {
                use core::fmt::Write;
                use musesoc_firmware::log::format_nostd::BufferWriter;
                use musesoc_firmware::log::format_nostd::SIZE;
                let mut buffer = [0u8; SIZE];
                let mut writer = BufferWriter::new(buffer);
                write!(&mut writer, $($arg)*).unwrap();
                writer
            }
        };
    }
    pub use _format as format;

    pub struct BufferWriter {
        buffer: [u8; SIZE],
        cursor: usize,
    }

    impl BufferWriter {
        pub fn new(buffer: [u8; SIZE]) -> Self {
            BufferWriter { buffer, cursor: 0 }
        }

        pub fn reset(&mut self) {
            self.cursor = 0;
        }

        pub fn as_bytes(&self) -> &[u8] {
            &self.buffer[0..self.cursor]
        }

        pub fn as_str(&self) -> &str {
            core::str::from_utf8(&self.buffer[0..self.cursor]).expect("invalid utf-8 string")
        }
    }

    impl core::fmt::Write for BufferWriter {
        fn write_str(&mut self, s: &str) -> core::fmt::Result {
            let len = self.buffer.len();
            for (i, &b) in self.buffer[self.cursor..len]
                .iter_mut()
                .zip(s.as_bytes().iter())
            {
                *i = b;
            }
            self.cursor = usize::min(len, self.cursor + s.as_bytes().len());
            Ok(())
        }
    }
}

pub use format_nostd::format;

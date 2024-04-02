import * as React from 'react';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import AlertTitle from '@mui/material/AlertTitle';
import CloseIcon from '@mui/icons-material/Close';

/**
 * Error Dialog
 *
 * @param {{open: boolean, handleClose: function, errors: Array}} props
 */
const ErrorDialog = ({ open, handleClose, errors=[] }) => {
    if (!errors) {
        return null;
    }

    return (
        <Box sx={{
            position: 'fixed',
            margin: '2vw',
            top: 10,
            left: 0,
            right: 0,
            zIndex: 1000,
        }}>
            <Collapse in={open}>
                {errors.map((error, index) => (
                    <Alert
                        key={index}
                        severity="error"
                        action={
                            <IconButton
                                aria-label="close"
                                color="inherit"
                                size="small"
                                onClick={() => handleClose(index)}
                            >
                                <CloseIcon fontSize="inherit" />
                            </IconButton>
                        }
                        sx={{ mb: 2 }}>
                        <AlertTitle>Error {error.type}</AlertTitle>
                        {error.message}
                    </Alert>
                ))}
            </Collapse>
        </Box>
      );
}

export default React.memo(ErrorDialog);
